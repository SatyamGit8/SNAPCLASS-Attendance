import streamlit as st
import time
from datetime import datetime
import numpy as np
import pandas as pd
from PIL import Image

from src.ui.base_layout import style_background_dashboard, style_base_layout
from src.components.header import header_dashboard
from src.components.footer import footer_dashboard
from src.components.dialog_enroll import enroll_dialog
from src.components.subject_card import subject_card
from src.pipelines.face_pipeline import predict_attendance, get_face_embeddings, train_classifier
from src.pipelines.voice_pipeline import get_voice_embedding
from src.database.db import (
    get_all_students,
    create_student,
    get_student_subjects,
    get_student_attendance,
    unenroll_student_to_subject
)


def student_dashboard():
    student_data = st.session_state.student_data
    student_id = student_data['student_id']

    # Modern Navbar
    nav_c1, nav_c2 = st.columns([3, 1], vertical_alignment='center')
    with nav_c1:
        header_dashboard()
    with nav_c2:
        if st.button("Log Out", type='secondary', width='stretch', icon=':material/logout:'):
            st.session_state['is_logged_in'] = False
            del st.session_state.student_data
            st.rerun()

    st.markdown("<hr style='margin: 1rem 0 1.5rem 0;'>", unsafe_allow_html=True)

    # Student Welcome Banner
    st.markdown(
        f"""
        <div style="background: linear-gradient(135deg, #1E3A8A 0%, #2563EB 100%); border-radius: 14px; padding: 1.5rem 1.75rem; color: #FFFFFF; margin-bottom: 1.5rem; box-shadow: 0 4px 14px rgba(37,99,235,0.15);">
            <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:10px;">
                <div>
                    <span style="background: rgba(255,255,255,0.2); color:#FFFFFF; font-size:0.75rem; font-weight:700; padding:3px 10px; border-radius:9999px; text-transform:uppercase; letter-spacing:0.05em;">Student Account</span>
                    <h2 style="color:#FFFFFF !important; font-size:1.75rem; margin:0.35rem 0 0.15rem 0; font-weight:800;">Welcome, {student_data['name']}</h2>
                    <p style="color:#BFDBFE; font-size:0.875rem; margin:0;">Student ID: #{student_id} • Biometric FaceID & Voice Verified</p>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    with st.spinner('Loading enrolled subjects and records...'):
        subjects = get_student_subjects(student_id)
        logs = get_student_attendance(student_id)

    # Compute stats
    stats_map = {}
    total_classes = 0
    total_attended = 0

    for log in logs:
        sid = log['subject_id']
        if sid not in stats_map:
            stats_map[sid] = {"total": 0, "attended": 0}

        stats_map[sid]['total'] += 1
        total_classes += 1

        if log.get('is_present'):
            stats_map[sid]['attended'] += 1
            total_attended += 1

    overall_rate = round((total_attended / total_classes * 100), 1) if total_classes > 0 else 0.0

    # Metric Row
    m1, m2, m3 = st.columns(3)
    with m1:
        st.metric("Enrolled Courses", len(subjects))
    with m2:
        st.metric("Overall Attendance", f"{overall_rate}%")
    with m3:
        st.metric("Classes Attended", f"{total_attended} / {total_classes}")

    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

    # Subjects Header & Action
    sub_c1, sub_c2 = st.columns([3, 1], vertical_alignment='center')
    with sub_c1:
        st.subheader("Your Enrolled Courses")
        st.caption("Active subjects registered to your profile.")
    with sub_c2:
        if st.button("➕ Enroll New Course", type='primary', width='stretch'):
            enroll_dialog()

    if not subjects:
        st.markdown(
            """
            <div style="background:#FFFFFF; border:1px dashed #CBD5E1; border-radius:14px; padding:2.5rem; text-align:center; margin-top:1rem;">
                <p style="font-size:1.1rem; font-weight:600; color:#1E293B; margin-bottom:0.25rem;">No courses enrolled yet</p>
                <p style="font-size:0.875rem; color:#64748B; margin-bottom:1rem;">Ask your instructor for a course invite code or click 'Enroll New Course' above.</p>
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        cols = st.columns(2)
        for i, sub_node in enumerate(subjects):
            sub = sub_node.get('subjects')
            if not sub:
                continue
            sid = sub['subject_id']
            stats = stats_map.get(sid, {"total": 0, "attended": 0})

            def make_unenroll(course_id, course_name):
                def unenroll_button():
                    if st.button("Unenroll Course", key=f"unenroll_{course_id}", type='tertiary', width='stretch', icon=':material/delete:'):
                        unenroll_student_to_subject(student_id, course_id)
                        st.toast(f'Unenrolled from {course_name} successfully!', icon="ℹ️")
                        st.rerun()
                return unenroll_button

            with cols[i % 2]:
                subject_card(
                    name=sub['name'],
                    code=sub['subject_code'],
                    section=sub['section'],
                    stats=[
                        ('📅', 'Total', stats['total']),
                        ('✅', 'Attended', stats['attended']),
                    ],
                    footer_callback=make_unenroll(sid, sub['name'])
                )

    # Detailed Attendance History Table
    if logs:
        st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
        with st.expander("📋 Detailed Attendance History Logs", expanded=False):
            history_data = []
            for log in logs:
                sub = log.get('subjects') or {}
                ts = log.get('timestamp')
                history_data.append({
                    "Subject": sub.get('name', 'N/A'),
                    "Code": sub.get('subject_code', 'N/A'),
                    "Section": sub.get('section', 'N/A'),
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

    # Top Navbar
    top_c1, top_c2 = st.columns([3, 1], vertical_alignment='center')
    with top_c1:
        header_dashboard()
    with top_c2:
        if st.button("← Back to Home", type='secondary', width='stretch'):
            st.session_state['login_type'] = None
            st.rerun()

    st.markdown("<hr style='margin: 1rem 0 1.5rem 0;'>", unsafe_allow_html=True)

    # Join Code Alert if present
    pending_code = st.session_state.get('pending_join_code') or st.query_params.get('join-code')
    if pending_code:
        st.info(f"🎓 **Classroom Invite:** You are joining class code **`{pending_code}`**. Log in with FaceID or register below to complete enrollment automatically.")

    # Centered Layout for Login & Registration
    center_col1, center_col2, center_col3 = st.columns([1, 8, 1])

    with center_col2:
        with st.container(border=True):
            st.markdown(
                """
                <div style="margin-bottom: 1.25rem;">
                    <div style="display:flex; align-items:center; gap:8px;">
                        <span class="saas-badge-brand">Student Portal</span>
                    </div>
                    <h2 style="font-size:1.6rem; color:#0F172A; margin:0.35rem 0 0.15rem 0;">Student Authentication</h2>
                    <p style="color:#64748B; font-size:0.9rem; margin:0;">Access your courses using smart FaceID biometric recognition.</p>
                </div>
                """,
                unsafe_allow_html=True
            )

            portal_tab_login, portal_tab_reg = st.tabs(["🔑 FaceID Sign In", "📝 New Student Registration"])

            # ---------------- TAB 1: LOGIN ----------------
            with portal_tab_login:
                st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
                st.caption("📷 Verify your face to log in. Please face the camera directly in a well-lit environment.")

                login_tabs = st.tabs(["📸 Take Selfie / Upload Photo", "🎥 Live Webcam"])
                login_upload = None
                login_cam = None

                with login_tabs[0]:
                    st.caption("Upload a clear selfie (JPG, JPEG, PNG - Max 10MB)")
                    login_upload = st.file_uploader("Choose selfie photo", type=['jpg', 'jpeg', 'png'], key="login_face_upload")

                with login_tabs[1]:
                    st.caption("💡 Camera blocked? Click the camera icon in your browser address bar to **Allow** access.")
                    try:
                        login_cam = st.camera_input("Position face in center", key="login_face_cam")
                    except Exception:
                        st.warning("Webcam permission denied. Please use the 'Upload Photo' tab.")

                login_photo = login_upload if login_upload is not None else login_cam

                if login_photo:
                    try:
                        login_photo.seek(0)
                        img = np.array(Image.open(login_photo).convert('RGB'))
                    except Exception as e:
                        st.error(f"Error reading image: {e}")
                        img = None

                    if img is not None:
                        with st.spinner('Scanning face biometric features...'):
                            detected, all_ids, num_faces = predict_attendance(img)

                            if num_faces == 0:
                                st.warning('⚠️ No face detected. Please ensure your face is well-lit and facing forward.')
                            elif num_faces > 1:
                                st.warning('⚠️ Multiple faces detected. Please submit a single-person selfie.')
                            elif detected:
                                student_id = list(detected.keys())[0]
                                all_students = get_all_students()
                                student = next((s for s in all_students if s['student_id'] == student_id), None)

                                if student:
                                    st.session_state.is_logged_in = True
                                    st.session_state.user_role = 'student'
                                    st.session_state.student_data = student
                                    st.toast(f'Welcome back, {student["name"]}!', icon="👋")
                                    time.sleep(1)
                                    st.rerun()
                            else:
                                st.warning("❌ **Face not recognized.** If you haven't registered yet, please switch to the **'New Student Registration'** tab above.")

            # ---------------- TAB 2: REGISTER ----------------
            with portal_tab_reg:
                st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
                st.caption("Create your profile with FaceID and optional Voice biometric profile.")

                reg_name = st.text_input("Full Name", placeholder="e.g. Akash Sharma", key="reg_student_name")

                st.markdown("##### 1. Face Biometric Photo")
                reg_tabs = st.tabs(["📸 Take Selfie / Upload Photo", "🎥 Live Webcam"])
                reg_upload = None
                reg_cam = None

                with reg_tabs[0]:
                    st.caption("Upload a single clear headshot (JPG, JPEG, PNG)")
                    reg_upload = st.file_uploader("Upload headshot photo", type=['jpg', 'jpeg', 'png'], key="reg_face_upload")

                with reg_tabs[1]:
                    st.caption("💡 Camera blocked? Click the camera icon in browser address bar to **Allow**.")
                    try:
                        reg_cam = st.camera_input("Capture headshot", key="reg_face_cam")
                    except Exception:
                        st.warning("Camera permission denied. Use the 'Upload Photo' tab.")

                reg_photo = reg_upload if reg_upload is not None else reg_cam

                st.markdown("##### 2. Optional: Voice Enrollment")
                st.caption("Record 5–10 seconds saying: *'Hello, my name is [Your Name]. I am present.'*")

                reg_audio = None
                try:
                    reg_audio = st.audio_input("Record voice sample", key="reg_student_audio")
                except Exception:
                    st.warning("Audio recording is not supported in this browser.")

                st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

                if st.button("✨ Complete Registration", type="primary", width="stretch", disabled=not reg_name or not reg_photo):
                    if not reg_name.strip():
                        st.warning("Please enter your full name.")
                    elif not reg_photo:
                        st.warning("Please provide a face photo.")
                    else:
                        with st.spinner("Extracting biometric features & saving profile..."):
                            reg_photo.seek(0)
                            img = np.array(Image.open(reg_photo).convert('RGB'))
                            encodings = get_face_embeddings(img)

                            if not encodings:
                                st.error("No face detected in the photo. Please make sure your face is clearly visible and well-lit.")
                            elif len(encodings) > 1:
                                st.error("Multiple faces detected. Please upload a photo with only one person.")
                            else:
                                face_emb = encodings[0].tolist()

                                voice_emb = None
                                if reg_audio is not None:
                                    with st.spinner("Extracting voice features..."):
                                        try:
                                            voice_emb = get_voice_embedding(reg_audio.read())
                                        except Exception as ve:
                                            st.warning(f"Voice embedding could not be generated: {ve}")

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
                                    st.error("Failed to save student profile. Please check database connection.")

    footer_dashboard()