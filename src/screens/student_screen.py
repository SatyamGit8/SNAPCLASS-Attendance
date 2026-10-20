import streamlit as st

from src.ui.base_layout import style_background_dashboard, style_base_layout

from src.components.header import header_dashboard
from src.components.footer import footer_dashboard
from PIL import Image
import numpy as np
from src.pipelines.face_pipeline import predict_attendance, get_face_embeddings, train_classifier
from src.pipelines.voice_pipeline import get_voice_embedding
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

    c1, c2 =st.columns(2)
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
            stats_map[sid] = {"total":0, "attended": 0}

        stats_map[sid]['total'] +=1

        if log.get('is_present'):
            stats_map[sid]['attended'] += 1


    cols = st.columns(2)
    for i, sub_node in enumerate(subjects):
        sub = sub_node['subjects']
        sid = sub['subject_id']


        stats = stats_map.get(sid,{"total":0, "attended": 0} )
        def unenroll_button():
                if st.button("Unenroll from tihs course", type='tertiary', width='stretch', icon=':material/delete_forever:'):
                    unenroll_student_to_subject(student_id, sid)
                    st.toast(f'Unenrolled from {sub['name']} successfully!')
                    st.rerun()

        with cols[i % 2]:

            subject_card(
                name = sub['name'],
                code =sub['subject_code'],
                section = sub['section'],
                stats = [
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

    st.header('Login using FaceID', text_alignment='center')
    st.space()

    pending_code = st.session_state.get('pending_join_code') or st.query_params.get('join-code')
    if pending_code:
        st.info(f"🎓 **Class Invitation:** You are joining class code **`{pending_code}`**. Please scan your face to log in or register, and you will be enrolled automatically!")

    st.space()
    
    show_registration = st.session_state.get('show_registration', False)

    tab_upload, tab_camera = st.tabs(["📸 Take Selfie / Upload Photo (Recommended for Mobile)", "🎥 Live Webcam"])

    upload_file = None
    cam_file = None

    with tab_upload:
        st.caption("📱 **For Mobile:** Tap below to take a selfie using your phone camera or select a photo.")
        upload_file = st.file_uploader("Take a selfie or select a photo", type=['jpg', 'jpeg', 'png'], key="student_face_upload")

    with tab_camera:
        st.caption("💻 **For Laptops:** Use your built-in webcam.")
        try:
            cam_file = st.camera_input("Position your face in the center", key="student_face_cam")
        except Exception:
            st.warning("Webcam access not allowed. Please use the 'Take Selfie / Upload Photo' tab above.")

    photo_source = upload_file if upload_file is not None else cam_file

    if photo_source:
        try:
            photo_source.seek(0)
            pil_img = Image.open(photo_source).convert('RGB')
            img = np.array(pil_img)
            st.session_state['last_scanned_img'] = img
        except Exception as e:
            st.error(f"Error reading image: {e}")
            img = None

        if img is not None:
            with st.spinner('AI is scanning..'):
                detected, all_ids, num_faces = predict_attendance(img)

                if num_faces == 0:
                    st.warning('Face not found! Please ensure your face is clearly visible and well-lit.')
                elif num_faces > 1:
                    st.warning('Multiple faces found. Please take a photo with only one person.')
                else:
                    if detected:
                        student_id = list(detected.keys())[0]
                        all_students = get_all_students()
                        student = next((s for s in all_students if s['student_id'] == student_id), None)

                        if student:
                            st.session_state.is_logged_in = True
                            st.session_state.user_role = 'student'
                            st.session_state.student_data = student
                            st.session_state['show_registration'] = False
                            st.toast(f'Welcome Back {student["name"]}!')
                            time.sleep(1)
                            st.rerun()
                    else:
                        st.info('Face not recognized! You might be a new student!')
                        show_registration = True
                        st.session_state['show_registration'] = True

    if show_registration:
        with st.container(border=True):
            st.header('Register new Profile')
            new_name = st.text_input("Enter your name", placeholder='E.g. Hamza Rizvi')

            st.subheader('Optional : Voice Enrollment')
            st.info("Enroll for voice attendance (optional)")

            audio_data = None
            try:
                audio_data = st.audio_input('Record a short phrase like: "I am present, my name is..."')
            except Exception:
                pass

            if st.button('Create Account', type='primary'):
                if new_name:
                    with st.spinner('Creating profile..'):
                        img = st.session_state.get('last_scanned_img')
                        if img is None and photo_source is not None:
                            photo_source.seek(0)
                            img = np.array(Image.open(photo_source).convert('RGB'))

                        encodings = None
                        if img is not None:
                            encodings = get_face_embeddings(img)
                        if encodings:
                            face_emb = encodings[0].tolist()

                            voice_emb = None
                            if audio_data:
                                try:
                                    voice_emb = get_voice_embedding(audio_data.read())
                                except Exception as ve:
                                    st.warning(f"Voice enrollment skipped due to processing error: {ve}")

                            response_data = create_student(new_name, face_embedding=face_emb, voice_embedding=voice_emb)

                            if response_data:
                                train_classifier()
                                st.session_state.is_logged_in = True
                                st.session_state.user_role = 'student'
                                st.session_state.student_data = response_data[0]
                                st.toast(f'Profile Created! Hi {new_name}!')
                                time.sleep(1)
                                st.rerun()
                            else:
                                st.error('Failed to create student account in database. Please try again.')
                        else:
                            st.error('Could not capture your facial features for registration. Please face the camera directly.')

                else:
                    st.warning('Please enter your name!')


        
    footer_dashboard()