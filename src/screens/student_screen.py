import streamlit as st

from src.ui.base_layout import style_background_dashboard, style_base_layout

from src.components.header import header_dashboard
from src.components.footer import footer_dashboard
from PIL import Image
import numpy as np
from src.pipelines.face_pipeline import predict_attendance, get_face_embeddings, train_classifier
from src.database.db import get_all_students, create_student, get_student_subjects, get_student_attendance, unenroll_student_to_subject
import time

from src.components.dialog_enroll import enroll_dialog
from src.components.subject_card import subject_card


def student_dashboard():
    student_data = st.session_state.student_data
    student_id = student_data['student_id']
    c1, c2 = st.columns(2, vertical_alignment='center', gap='xxlarge')
    with c1:
        header_dashboard()
    with c2:
        st.subheader(f"""Welcome, {student_data['name']} """)
        if st.button("Logout", type='secondary', key='loginbackbtn', shortcut="control+backspace"):
            st.session_state['is_logged_in'] = False
            del st.session_state.student_data
            st.rerun()

    st.space()

    c1, c2 = st.columns(2)
    with c1:
        st.header('Your Enrolled Subjects')
    with c2:
        if st.button('Enroll in Subject', type='primary', width='stretch'):
            enroll_dialog()

    st.divider()

    with st.spinner('Loading your enrolled subjects..'):
        subjects = get_student_subjects(student_id)
        logs = get_student_attendance(student_id)

    stats_map = {}

    for log in logs:
        sid = log['subject_id']

        if sid not in stats_map:
            stats_map[sid] = {"total": 0, "attended": 0}

        stats_map[sid]['total'] += 1

        if log.get('is_present'):
            stats_map[sid]['attended'] += 1

    cols = st.columns(2)
    for i, sub_node in enumerate(subjects):
        sub = sub_node.get('subjects')
        if not sub:
            continue
        sid = sub['subject_id']

        stats = stats_map.get(sid, {"total": 0, "attended": 0})

        def unenroll_button():
            if st.button("Unenroll from this course", type='tertiary', width='stretch', icon=':material/delete_forever:'):
                unenroll_student_to_subject(student_id, sid)
                st.toast(f'Unenrolled from {sub["name"]} successfully!')
                st.rerun()

        with cols[i % 2]:
            subject_card(
                name=sub['name'],
                code=sub['subject_code'],
                section=sub['section'],
                stats=[
                    ('📅', 'Total', stats['total']),
                    ('✅', 'Attended', stats['attended']),
                ],
                footer_callback=unenroll_button
            )
    footer_dashboard()


def student_screen():
    style_background_dashboard()
    style_base_layout()

    if "student_data" in st.session_state:
        student_dashboard()
        return

    c1, c2 = st.columns(2, vertical_alignment='center', gap='xxlarge')
    with c1:
        header_dashboard()
    with c2:
        if st.button("Go back to Home", type='secondary', key='loginbackbtn', shortcut="control+backspace"):
            st.session_state['login_type'] = None
            st.rerun()

    st.header('Student Portal', text_alignment='center')

    pending_code = st.session_state.get('pending_join_code') or st.query_params.get('join-code')
    if pending_code:
        st.info(f"🎓 **Class Invitation:** You are joining class code **`{pending_code}`**. Log in with your FaceID or register below to complete enrollment automatically!")

    st.space()

    portal_tab_login, portal_tab_reg = st.tabs(["🔑 FaceID Login (Existing Student)", "📝 Register as New Student"])

    # ---------------- TAB 1: LOGIN ----------------
    with portal_tab_login:
        st.subheader("FaceID Login")
        st.caption("Verify your face to sign in and view your attendance records.")

        login_tabs = st.tabs(["📸 Take Selfie / Upload Photo", "🎥 Live Webcam"])
        login_upload = None
        login_cam = None

        with login_tabs[0]:
            login_upload = st.file_uploader("Upload selfie or photo", type=['jpg', 'jpeg', 'png'], key="login_face_upload")
        with login_tabs[1]:
            st.caption("💡 Camera access blocked? Address bar me upar camera icon par click karke **Allow** karein aur reload karein.")
            try:
                login_cam = st.camera_input("Position face in center", key="login_face_cam")
            except Exception:
                st.warning("Camera permission denied. Use the 'Upload Photo' tab.")

        login_photo = login_upload if login_upload is not None else login_cam

        if login_photo:
            try:
                login_photo.seek(0)
                img = np.array(Image.open(login_photo).convert('RGB'))
            except Exception as e:
                st.error(f"Error reading image: {e}")
                img = None

            if img is not None:
                with st.spinner('Verifying your FaceID...'):
                    detected, all_ids, num_faces = predict_attendance(img)

                    if num_faces == 0:
                        st.warning('Face not found! Please ensure your face is well-lit and facing the camera.')
                    elif num_faces > 1:
                        st.warning('Multiple faces detected. Please upload a photo with only one person.')
                    elif detected:
                        student_id = list(detected.keys())[0]
                        all_students = get_all_students()
                        student = next((s for s in all_students if s['student_id'] == student_id), None)

                        if student:
                            st.session_state.is_logged_in = True
                            st.session_state.user_role = 'student'
                            st.session_state.student_data = student
                            st.toast(f'Welcome Back {student["name"]}!', icon="👋")
                            time.sleep(1)
                            st.rerun()
                    else:
                        st.warning("❌ **Face not recognized.** If you haven't registered yet, please switch to the **'📝 Register as New Student'** tab above!")

    # ---------------- TAB 2: REGISTER ----------------
    with portal_tab_reg:
        st.subheader("Register New Student FaceID")
        st.caption("Enter your name and take a clear photo of your face to create your account.")

        reg_name = st.text_input("Full Name", placeholder="E.g. Akash Sharma", key="reg_student_name")

        reg_tabs = st.tabs(["📸 Take Selfie / Upload Photo", "🎥 Live Webcam"])
        reg_upload = None
        reg_cam = None

        with reg_tabs[0]:
            reg_upload = st.file_uploader("Upload your face photo", type=['jpg', 'jpeg', 'png'], key="reg_face_upload")
        with reg_tabs[1]:
            st.caption("💡 Camera access blocked? Address bar me upar camera icon par click karke **Allow** karein aur reload karein.")
            try:
                reg_cam = st.camera_input("Capture face photo", key="reg_face_cam")
            except Exception:
                st.warning("Camera permission denied. Use the 'Upload Photo' tab.")

        reg_photo = reg_upload if reg_upload is not None else reg_cam

        if st.button("✨ Register My FaceID Account", type="primary", width="stretch", disabled=not reg_name or not reg_photo):
            if not reg_name.strip():
                st.warning("Please enter your full name!")
            elif not reg_photo:
                st.warning("Please upload or capture your face photo!")
            else:
                with st.spinner("Extracting FaceID features & creating profile..."):
                    reg_photo.seek(0)
                    img = np.array(Image.open(reg_photo).convert('RGB'))
                    encodings = get_face_embeddings(img)

                    if not encodings:
                        st.error("Could not detect any face in the photo. Please make sure your face is clearly visible and well-lit.")
                    elif len(encodings) > 1:
                        st.error("Multiple faces detected in registration photo. Please submit a single-person photo.")
                    else:
                        face_emb = encodings[0].tolist()
                        response_data = create_student(reg_name.strip(), face_embedding=face_emb, voice_embedding=None)

                        if response_data:
                            train_classifier()
                            st.session_state.is_logged_in = True
                            st.session_state.user_role = 'student'
                            st.session_state.student_data = response_data[0]
                            st.toast(f"FaceID Profile Created! Welcome, {reg_name.strip()}!", icon="🎉")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error("Failed to save student profile in database. Please check connection.")

    footer_dashboard()