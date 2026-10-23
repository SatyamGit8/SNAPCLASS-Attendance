import streamlit as st

from src.ui.base_layout import style_background_dashboard, style_base_layout

from src.components.header import header_dashboard
from src.components.footer import footer_dashboard
from PIL import Image
import numpy as np
from src.pipelines.face_pipeline import predict_attendance, get_face_embeddings, train_classifier, load_and_orient_image
from src.pipelines.voice_pipeline import get_voice_embedding
from src.database.db import get_all_students, create_student, get_student_subjects, get_student_attendance, unenroll_student_to_subject
import time
from datetime import datetime
import pandas as pd

from src.components.dialog_enroll import enroll_dialog
from src.components.subject_card import subject_card
from src.database.config import supabase


@st.dialog("📸 Enhance / Update FaceID")
def enhance_face_dialog(student_id):
    st.write("Add an extra photo (different angle, classroom lighting, or mobile selfie) so AI recognizes you under any condition!")

    enh_tab1, enh_tab2 = st.tabs(["📁 Upload Photo", "📸 Live Camera"])
    up_file = None
    cam_file = None
    with enh_tab1:
        up_file = st.file_uploader("Upload selfie or photo", type=['jpg', 'jpeg', 'png'], key="enh_face_up")
    with enh_tab2:
        cam_file = st.camera_input("Take photo", key="enh_face_cam")

    photo = up_file if up_file is not None else cam_file
    if photo:
        c1, c2 = st.columns(2)
        with c1:
            if st.button("➕ Add as Extra Angle (Recommended)", type="primary", width="stretch"):
                with st.spinner("Processing facial features..."):
                    img = load_and_orient_image(photo)
                    embs = get_face_embeddings(img)
                    if not embs:
                        st.error("No face detected. Please ensure good lighting and face clearly visible.")
                    else:
                        new_emb = embs[0].tolist()
                        res = supabase.table('students').select('face_embedding').eq('student_id', student_id).execute()
                        curr = (res.data[0].get('face_embedding') or []) if res.data else []
                        combined = curr + new_emb
                        supabase.table('students').update({'face_embedding': combined}).eq('student_id', student_id).execute()
                        train_classifier()
                        st.toast("Extra face profile added! Recognition accuracy enhanced!", icon="🎉")
                        time.sleep(1)
                        st.rerun()
        with c2:
            if st.button("🔄 Replace Primary Photo", type="secondary", width="stretch"):
                with st.spinner("Updating face profile..."):
                    img = load_and_orient_image(photo)
                    embs = get_face_embeddings(img)
                    if not embs:
                        st.error("No face detected. Please ensure good lighting and face clearly visible.")
                    else:
                        new_emb = embs[0].tolist()
                        supabase.table('students').update({'face_embedding': new_emb}).eq('student_id', student_id).execute()
                        train_classifier()
                        st.toast("FaceID photo updated successfully!", icon="✅")
                        time.sleep(1)
                        st.rerun()


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

    c1, c2, c3 = st.columns([1.6, 1, 1], vertical_alignment='bottom')
    with c1:
        st.header('Your Enrolled Subjects')
    with c2:
        if st.button('Enroll in Subject', type='primary', width='stretch'):
            enroll_dialog()
    with c3:
        if st.button('📸 Enhance FaceID', type='secondary', width='stretch'):
            enhance_face_dialog(student_id)

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
        sub_name = sub.get('name', 'Subject')

        stats = stats_map.get(sid, {"total": 0, "attended": 0})

        def make_unenroll_callback(curr_sid, curr_name):
            def _callback():
                if st.button(
                    "Unenroll from this course",
                    key=f"unenroll_btn_{student_id}_{curr_sid}",
                    type='tertiary',
                    width='stretch',
                    icon=':material/delete_forever:'
                ):
                    unenroll_student_to_subject(student_id, curr_sid)
                    st.toast(f'Unenrolled from {curr_name} successfully!')
                    st.rerun()
            return _callback

        with cols[i % 2]:
            subject_card(
                name=sub['name'],
                code=sub['subject_code'],
                section=sub['section'],
                stats=[
                    ('📅', 'Total', stats['total']),
                    ('✅', 'Attended', stats['attended']),
                ],
                footer_callback=make_unenroll_callback(sid, sub_name)
            )

    if logs:
        st.space()
        with st.expander("📅 View Detailed Attendance History", expanded=False):
            history_data = []
            for log in logs:
                sub = log.get('subjects') or {}
                ts = log.get('timestamp')
                history_data.append({
                    "Subject": sub.get('name', 'N/A'),
                    "Subject Code": sub.get('subject_code', 'N/A'),
                    "Date & Time": datetime.fromisoformat(ts).strftime("%Y-%m-%d %I:%M %p") if ts else "N/A",
                    "Status": "✅ Present" if log.get('is_present') else "❌ Absent"
                })
            st.dataframe(pd.DataFrame(history_data), width='stretch', hide_index=True)

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
        st.markdown("<h3 style='color: #EB459E; font-family: Outfit, sans-serif; font-weight: 700; margin-bottom: 2px;'>FaceID Login</h3>", unsafe_allow_html=True)
        st.caption("Verify your face to sign in and view your attendance records.")

        login_tabs = st.tabs(["📸 Take Selfie / Upload Photo", "🎥 Live Webcam"])
        login_upload = None
        login_cam = None

        with login_tabs[0]:
            st.caption("💡 **Mobile:** Yahan tap karke aap seedhe apne phone ke Camera se selfie le sakte hain ya gallery se photo chun sakte hain.")
            login_upload = st.file_uploader("Upload selfie or photo", type=['jpg', 'jpeg', 'png'], key="login_face_upload")
        with login_tabs[1]:
            st.info(
                "📷 **Camera Enable Guide:**\n\n"
                "- 📱 **Mobile Users (Chrome/Edge):** Upar address bar me baayein (left) taraf bane **`⊸` (Tune)** ya **`🔒` (Lock)** icon par tap karein ➔ **Permissions** ➔ **Camera: Allow** karein aur page reload karein.\n"
                "- 💻 **Laptop Users:** Address bar me upar right side me **Camera icon (red cross)** par click karke **Always allow** karein.\n"
                "- 💡 **Easy Mobile Option:** Agar live webcam stream na khule, to pehle tab **'📸 Take Selfie / Upload Photo'** par tap karein — wahan se phone camera seedhe chalega!"
            )
            try:
                login_cam = st.camera_input("Position face in center", key="login_face_cam")
            except Exception:
                st.warning("Camera permission denied. Use the 'Upload Photo' tab.")

        login_photo = login_upload if login_upload is not None else login_cam

        if login_photo:
            try:
                img = load_and_orient_image(login_photo)
            except Exception as e:
                st.error(f"Error reading image: {e}")
                img = None

            if img is not None:
                with st.spinner('Verifying your FaceID...'):
                    # Standard 0.60 tolerance for 1-person selfie verification (LFW benchmark)
                    detected, all_ids, num_faces = predict_attendance(img, tolerance=0.60)

                    if num_faces == 0:
                        st.warning('Face not found! Please ensure your face is well-lit, clearly visible and facing the camera.')
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
        st.markdown("<h3 style='color: #EB459E; font-family: Outfit, sans-serif; font-weight: 700; margin-bottom: 2px;'>Register New Profile (Face & Voice)</h3>", unsafe_allow_html=True)
        st.caption("Create your student profile with FaceID and optional Voice profile for seamless AI attendance.")

        reg_name = st.text_input("Enter your full name", placeholder="E.g. Hamza Rizvi", key="reg_student_name")

        st.markdown("<h5 style='color: #EB459E; font-family: Outfit, sans-serif; font-weight: 700; margin-top: 12px; margin-bottom: 4px;'>📸 Face Registration</h5>", unsafe_allow_html=True)
        reg_tabs = st.tabs(["📸 Take Selfie / Upload Photo", "🎥 Live Webcam"])
        reg_upload = None
        reg_cam = None

        with reg_tabs[0]:
            st.caption("💡 **Mobile:** Yahan tap karke phone camera se selfie lein ya gallery se photo upload karein.")
            reg_upload = st.file_uploader("Upload your face photo", type=['jpg', 'jpeg', 'png'], key="reg_face_upload")
        with reg_tabs[1]:
            st.info(
                "📷 **Camera Enable Guide:**\n\n"
                "- 📱 **Mobile Users (Chrome/Edge):** Upar address bar me baayein (left) taraf bane **`⊸` (Tune)** ya **`🔒` (Lock)** icon par tap karein ➔ **Permissions** ➔ **Camera: Allow** karein aur page reload karein.\n"
                "- 💻 **Laptop Users:** Address bar me upar right side me **Camera icon (red cross)** par click karke **Always allow** karein.\n"
                "- 💡 **Easy Mobile Option:** Agar live webcam stream na khule, to pehle tab **'📸 Take Selfie / Upload Photo'** par tap karein — wahan se phone camera seedhe chalega!"
            )
            try:
                reg_cam = st.camera_input("Capture face photo", key="reg_face_cam")
            except Exception:
                st.warning("Camera permission denied. Use the 'Upload Photo' tab.")

        reg_photo = reg_upload if reg_upload is not None else reg_cam
        if reg_photo:
            st.success("✅ Face photo ready!")

        st.space()
        st.markdown("<h5 style='color: #EB459E; font-family: Outfit, sans-serif; font-weight: 700; margin-top: 12px; margin-bottom: 4px;'>🎙️ Optional: Voice Enrollment</h5>", unsafe_allow_html=True)
        st.caption("Enroll your voice for voice-only attendance. Record a 5-10s voice e.g. *'Hello, this is my voice. My name is [Your Name]. I am present.'*")

        reg_audio = None
        try:
            reg_audio = st.audio_input("Record voice sample (5-10 seconds)", key="reg_student_audio")
        except Exception:
            st.warning("Audio recorder not available on this browser.")

        st.space()

        if st.button("✨ Create Account", type="primary", width="stretch", disabled=not reg_name or not reg_photo):
            if not reg_name.strip():
                st.warning("Please enter your full name!")
            elif not reg_photo:
                st.warning("Please upload or capture your face photo!")
            else:
                with st.spinner("Creating profile & extracting facial features..."):
                    try:
                        img = load_and_orient_image(reg_photo)
                    except Exception as e:
                        st.error(f"Error reading image: {e}")
                        img = None

                    if img is not None:
                        encodings = get_face_embeddings(img)

                    if not encodings:
                        st.error("Could not detect any face in the photo. Please make sure your face is clearly visible and well-lit.")
                    elif len(encodings) > 1:
                        st.error("Multiple faces detected in registration photo. Please submit a single-person photo.")
                    else:
                        face_emb = encodings[0].tolist()

                        voice_emb = None
                        if reg_audio is not None:
                            with st.spinner("Extracting voice features..."):
                                try:
                                    voice_emb = get_voice_embedding(reg_audio.read())
                                except Exception as ve:
                                    st.warning(f"Could not process voice sample: {ve}")

                        response_data = create_student(reg_name.strip(), face_embedding=face_emb, voice_embedding=voice_emb)

                        if response_data:
                            train_classifier()
                            st.session_state.is_logged_in = True
                            st.session_state.user_role = 'student'
                            st.session_state.student_data = response_data[0]
                            success_msg = f"Profile Created with FaceID{' & Voice' if voice_emb else ''}! Welcome, {reg_name.strip()}!"
                            st.toast(success_msg, icon="🎉")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error("Failed to save student profile in database. Please check connection.")

    footer_dashboard()