import time
from datetime import datetime
import numpy as np
import pandas as pd
import streamlit as st

from src.ui.base_layout import style_background_dashboard, style_base_layout
from src.components.header import header_dashboard
from src.components.footer import footer_dashboard
from src.components.subject_card import subject_card
from src.database.db import (
    check_teacher_exists,
    create_teacher,
    teacher_login,
    get_teacher_subjects,
    get_attendance_for_teacher
)
from src.components.dialog_create_subject import create_subject_dialog
from src.components.dialog_share_subject import share_subject_dialog
from src.components.dialog_add_photo import add_photos_dialog
from src.components.dialog_voice_attendance import voice_attendance_dialog
from src.pipelines.face_pipeline import predict_attendance
from src.components.dialog_attendance_results import attendance_result_dialog
from src.database.config import supabase


def teacher_screen():
    style_background_dashboard()
    style_base_layout()

    if "teacher_data" in st.session_state:
        teacher_dashboard()
    elif 'teacher_login_type' not in st.session_state or st.session_state.teacher_login_type == "login":
        teacher_screen_login()
    elif st.session_state.teacher_login_type == "register":
        teacher_screen_register()


def teacher_dashboard():
    teacher_data = st.session_state.teacher_data
    teacher_id = teacher_data['teacher_id']

    # Modern Navbar
    nav_c1, nav_c2 = st.columns([3, 1], vertical_alignment='center')
    with nav_c1:
        header_dashboard()
    with nav_c2:
        if st.button("Log Out", type='secondary', width='stretch', icon=':material/logout:'):
            st.session_state['is_logged_in'] = False
            del st.session_state.teacher_data
            st.rerun()

    st.markdown("<hr style='margin: 1rem 0 1.5rem 0;'>", unsafe_allow_html=True)

    # Faculty Banner
    st.markdown(
        f"""
        <div style="background: linear-gradient(135deg, #0F172A 0%, #1E3A8A 100%); border-radius: 14px; padding: 1.5rem 1.75rem; color: #FFFFFF; margin-bottom: 1.5rem; box-shadow: 0 4px 14px rgba(15,23,42,0.15);">
            <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:10px;">
                <div>
                    <span style="background: rgba(255,255,255,0.15); color:#FFFFFF; font-size:0.75rem; font-weight:700; padding:3px 10px; border-radius:9999px; text-transform:uppercase; letter-spacing:0.05em;">Faculty Portal</span>
                    <h2 style="color:#FFFFFF !important; font-size:1.75rem; margin:0.35rem 0 0.15rem 0; font-weight:800;">Welcome, Prof. {teacher_data['name']}</h2>
                    <p style="color:#94A3B8; font-size:0.875rem; margin:0;">Faculty ID: #{teacher_id} • Smart Attendance Management Suite</p>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    if "current_teacher_tab" not in st.session_state:
        st.session_state.current_teacher_tab = 'take_attendance'

    # Clean Tab Navigation
    tab1, tab2, tab3 = st.columns(3)

    with tab1:
        type1 = "primary" if st.session_state.current_teacher_tab == 'take_attendance' else "secondary"
        if st.button('📸 Take Attendance', type=type1, width='stretch'):
            st.session_state.current_teacher_tab = 'take_attendance'
            st.rerun()

    with tab2:
        type2 = "primary" if st.session_state.current_teacher_tab == 'manage_subjects' else "secondary"
        if st.button('📚 Manage Courses', type=type2, width='stretch'):
            st.session_state.current_teacher_tab = 'manage_subjects'
            st.rerun()

    with tab3:
        type3 = "primary" if st.session_state.current_teacher_tab == 'attendance_records' else "secondary"
        if st.button('📊 Attendance Reports', type=type3, width='stretch'):
            st.session_state.current_teacher_tab = 'attendance_records'
            st.rerun()

    st.markdown("<hr style='margin: 1rem 0 1.5rem 0;'>", unsafe_allow_html=True)

    if st.session_state.current_teacher_tab == "take_attendance":
        teacher_tab_take_attendance()
    elif st.session_state.current_teacher_tab == "manage_subjects":
        teacher_tab_manage_subjects()
    elif st.session_state.current_teacher_tab == "attendance_records":
        teacher_tab_attendance_records()

    footer_dashboard()


def teacher_tab_take_attendance():
    teacher_id = st.session_state.teacher_data['teacher_id']

    if 'attendance_images' not in st.session_state:
        st.session_state.attendance_images = []

    subjects = get_teacher_subjects(teacher_id)

    if not subjects:
        st.markdown(
            """
            <div style="background:#FFFFFF; border:1px dashed #CBD5E1; border-radius:14px; padding:2.5rem; text-align:center;">
                <h4 style="color:#1E293B; margin-bottom:0.5rem;">No Courses Available</h4>
                <p style="color:#64748B; font-size:0.9rem;">You haven't created any courses yet. Please switch to 'Manage Courses' to create your first class.</p>
            </div>
            """,
            unsafe_allow_html=True
        )
        return

    subject_options = {f"{s['name']} ({s['subject_code']}) - Sec {s['section']}": s['subject_id'] for s in subjects}

    # Top Control Bar
    with st.container(border=True):
        col1, col2 = st.columns([3, 1], vertical_alignment='center')
        with col1:
            selected_subject_label = st.selectbox('Select Course for Attendance', options=list(subject_options.keys()))
        with col2:
            st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
            if st.button('➕ Add Class Photos', type='primary', width='stretch'):
                add_photos_dialog()

    selected_subject_id = subject_options[selected_subject_label]

    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

    # Photo Gallery Display
    has_photos = bool(st.session_state.attendance_images)

    if has_photos:
        st.subheader(f"Classroom Photos ({len(st.session_state.attendance_images)} Uploaded)")
        st.caption("AI will scan all faces across these photos to detect present students.")
        gallery_cols = st.columns(4)
        for idx, img in enumerate(st.session_state.attendance_images):
            with gallery_cols[idx % 4]:
                st.image(img, width='stretch', caption=f'Photo #{idx+1}')

    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

    # Actions Row
    c1, c2, c3 = st.columns(3)

    with c1:
        if st.button('🗑️ Clear All Photos', width='stretch', type='tertiary', disabled=not has_photos):
            st.session_state.attendance_images = []
            st.rerun()

    with c2:
        if st.button('🔍 Run Face Recognition', width='stretch', type='primary', disabled=not has_photos):
            with st.spinner('Scanning classroom photos and matching face embeddings...'):
                all_detected_ids = {}

                for idx, img in enumerate(st.session_state.attendance_images):
                    img_np = np.array(img.convert('RGB'))
                    detected, _, _ = predict_attendance(img_np)

                    if detected:
                        for sid in detected.keys():
                            student_id = int(sid)
                            all_detected_ids.setdefault(student_id, []).append(f"Photo #{idx+1}")

                enrolled_res = supabase.table('subject_students').select("*, students(*)").eq('subject_id', selected_subject_id).execute()
                enrolled_students = enrolled_res.data or []

                results, attendance_to_log = [], []

                if not enrolled_students:
                    st.warning('No students are enrolled in this course yet. Share the course code with your students first.')
                else:
                    current_timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

                    for node in enrolled_students:
                        student = node.get('students')
                        if not student:
                            continue
                        sources = all_detected_ids.get(int(student['student_id']), [])
                        is_present = len(sources) > 0

                        results.append({
                            "Name": student['name'],
                            "ID": student['student_id'],
                            "Detected In": ", ".join(sources) if is_present else "-",
                            "Status": "✅ Present" if is_present else "❌ Absent"
                        })

                        attendance_to_log.append({
                            'student_id': student['student_id'],
                            'subject_id': selected_subject_id,
                            'timestamp': current_timestamp,
                            'is_present': bool(is_present)
                        })

                    if results:
                        attendance_result_dialog(pd.DataFrame(results), attendance_to_log)
                    else:
                        st.warning('No valid enrolled student data found.')

    with c3:
        if st.button('🎙️ Voice Attendance', type='secondary', width='stretch'):
            voice_attendance_dialog(selected_subject_id)


def teacher_tab_manage_subjects():
    teacher_id = st.session_state.teacher_data['teacher_id']

    h_col1, h_col2 = st.columns([3, 1], vertical_alignment='center')
    with h_col1:
        st.subheader("Course Management")
        st.caption("Create courses and share invitation codes with your students.")
    with h_col2:
        if st.button('➕ Create New Course', type='primary', width='stretch'):
            create_subject_dialog(teacher_id)

    st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

    subjects = get_teacher_subjects(teacher_id)
    if subjects:
        cols = st.columns(2)
        for i, sub in enumerate(subjects):
            stats = [
                ("👥", "Students", sub.get('total_students', 0)),
                ("📅", "Lectures", sub.get('total_classes', 0)),
            ]

            def make_share(sub_name, sub_code):
                def share_btn():
                    if st.button(f"Share Code: {sub_code}", key=f"share_{sub_code}", type='secondary', width='stretch', icon=":material/share:"):
                        share_subject_dialog(sub_name, sub_code)
                return share_btn

            with cols[i % 2]:
                subject_card(
                    name=sub['name'],
                    code=sub['subject_code'],
                    section=sub['section'],
                    stats=stats,
                    footer_callback=make_share(sub['name'], sub['subject_code'])
                )
    else:
        st.markdown(
            """
            <div style="background:#FFFFFF; border:1px dashed #CBD5E1; border-radius:14px; padding:2.5rem; text-align:center;">
                <p style="font-size:1.1rem; font-weight:600; color:#1E293B; margin-bottom:0.25rem;">No courses created yet</p>
                <p style="font-size:0.875rem; color:#64748B;">Click 'Create New Course' to set up your first subject and section.</p>
            </div>
            """,
            unsafe_allow_html=True
        )


def teacher_tab_attendance_records():
    teacher_id = st.session_state.teacher_data['teacher_id']

    records = get_attendance_for_teacher(teacher_id)

    if not records:
        st.markdown(
            """
            <div style="background:#FFFFFF; border:1px dashed #CBD5E1; border-radius:14px; padding:2.5rem; text-align:center;">
                <p style="font-size:1.1rem; font-weight:600; color:#1E293B; margin-bottom:0.25rem;">No Attendance Records Found</p>
                <p style="font-size:0.875rem; color:#64748B;">Once you take attendance using Face or Voice, session logs will appear here.</p>
            </div>
            """,
            unsafe_allow_html=True
        )
        return

    data = []
    for r in records:
        ts = r.get('timestamp')
        student = r.get('students') or {}

        data.append({
            "ts_group": ts.split(".")[0] if ts else None,
            "Date & Time": datetime.fromisoformat(ts).strftime("%Y-%m-%d %I:%M %p") if ts else "N/A",
            "Subject": r['subjects']['name'],
            "Subject Code": r['subjects']['subject_code'],
            "Student Name": student.get('name', f"Student #{r.get('student_id')}"),
            "Student ID": r.get('student_id'),
            "is_present": bool(r.get('is_present', False)),
            "Status": "✅ Present" if r.get('is_present', False) else "❌ Absent"
        })

    df = pd.DataFrame(data)

    # Summary metrics across all records
    summary = (
        df.groupby(['ts_group', 'Date & Time', 'Subject', 'Subject Code'])
        .agg(
            Present_Count=('is_present', 'sum'),
            Total_Count=('is_present', 'count')
        ).reset_index()
    )

    summary['Attendance Rate'] = (
        (summary['Present_Count'] / summary['Total_Count'] * 100).round(1).astype(str) + "%"
    )

    summary['Stats'] = (
        summary['Present_Count'].astype(str) + " / " + summary['Total_Count'].astype(str) + ' Present'
    )

    total_sessions = len(summary)
    total_present_instances = int(df['is_present'].sum())
    total_instances = len(df)
    overall_avg = round((total_present_instances / total_instances * 100), 1) if total_instances > 0 else 0.0

    # Quick KPI Metric Cards
    k1, k2, k3 = st.columns(3)
    with k1:
        st.metric("Total Attendance Sessions", total_sessions)
    with k2:
        st.metric("Overall Attendance Rate", f"{overall_avg}%")
    with k3:
        st.metric("Total Present Logged", f"{total_present_instances} / {total_instances}")

    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

    # Session Summary Table
    st.subheader("📋 Session Summaries")
    display_df = (
        summary.sort_values(by='ts_group', ascending=False)
        [['Date & Time', 'Subject', 'Subject Code', 'Stats', 'Attendance Rate']]
    )
    st.dataframe(display_df, width='stretch', hide_index=True)

    st.markdown("<hr style='margin: 1.5rem 0;'>", unsafe_allow_html=True)

    # Detailed Student Breakdown per Session
    st.subheader("🔍 Detailed Student Presence per Session")
    st.caption("Inspect individual student attendance for any past session.")

    sessions = summary.sort_values(by='ts_group', ascending=False)
    session_options = {
        f"{row['Date & Time']} — {row['Subject']} ({row['Subject Code']})": row['ts_group']
        for _, row in sessions.iterrows()
    }

    if session_options:
        selected_session_label = st.selectbox("Select Session", options=list(session_options.keys()))
        selected_ts = session_options[selected_session_label]

        session_students = df[df['ts_group'] == selected_ts][['Student Name', 'Student ID', 'Status', 'Date & Time']]

        f_col1, f_col2 = st.columns([1, 3])
        with f_col1:
            filter_choice = st.radio("Status Filter", ["All", "Present Only", "Absent Only"], horizontal=True)

        if filter_choice == "Present Only":
            session_students = session_students[session_students['Status'] == "✅ Present"]
        elif filter_choice == "Absent Only":
            session_students = session_students[session_students['Status'] == "❌ Absent"]

        st.dataframe(session_students, width='stretch', hide_index=True)


def login_teacher(username, password):
    if not username or not password:
        return False
    teacher = teacher_login(username, password)
    if teacher:
        st.session_state.user_role = 'teacher'
        st.session_state.teacher_data = teacher
        st.session_state.is_logged_in = True
        return True
    return False


def teacher_screen_login():
    # Top Navbar
    top_c1, top_c2 = st.columns([3, 1], vertical_alignment='center')
    with top_c1:
        header_dashboard()
    with top_c2:
        if st.button("← Back to Home", type='secondary', width='stretch'):
            st.session_state['login_type'] = None
            st.rerun()

    st.markdown("<hr style='margin: 1rem 0 1.5rem 0;'>", unsafe_allow_html=True)

    center_c1, center_c2, center_c3 = st.columns([1, 6, 1])

    with center_c2:
        with st.container(border=True):
            st.markdown(
                """
                <div style="margin-bottom: 1.25rem;">
                    <span class="saas-badge-brand">Faculty Access</span>
                    <h2 style="font-size:1.6rem; color:#0F172A; margin:0.35rem 0 0.15rem 0;">Teacher Sign In</h2>
                    <p style="color:#64748B; font-size:0.9rem; margin:0;">Enter your faculty credentials to manage your courses and attendance.</p>
                </div>
                """,
                unsafe_allow_html=True
            )

            teacher_username = st.text_input("Username", placeholder='e.g. ananyaroy', key="teacher_login_user")
            teacher_pass = st.text_input("Password", type='password', placeholder="••••••••", key="teacher_login_pass")

            st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

            btnc1, btnc2 = st.columns(2)
            with btnc1:
                if st.button('Sign In', type='primary', width='stretch', icon=':material/login:'):
                    if login_teacher(teacher_username, teacher_pass):
                        st.toast("Welcome back!", icon="👋")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("Invalid username or password. Please try again.")

            with btnc2:
                if st.button('Register Account', type="secondary", width='stretch'):
                    st.session_state.teacher_login_type = 'register'
                    st.rerun()

    footer_dashboard()


def register_teacher(teacher_username, teacher_name, teacher_pass, teacher_pass_confirm):
    if not teacher_username or not teacher_name or not teacher_pass:
        return False, "All fields are required!"
    if check_teacher_exists(teacher_username):
        return False, "This username is already taken. Please choose another."
    if teacher_pass != teacher_pass_confirm:
        return False, "Passwords do not match."

    try:
        res = create_teacher(teacher_username, teacher_pass, teacher_name)
        if res:
            return True, "Account created successfully! Please sign in now."
        return False, "Failed to create account. Please check database permissions."
    except Exception as e:
        return False, f"Unexpected error: {e}"


def teacher_screen_register():
    top_c1, top_c2 = st.columns([3, 1], vertical_alignment='center')
    with top_c1:
        header_dashboard()
    with top_c2:
        if st.button("← Back to Home", type='secondary', width='stretch'):
            st.session_state['login_type'] = None
            st.rerun()

    st.markdown("<hr style='margin: 1rem 0 1.5rem 0;'>", unsafe_allow_html=True)

    center_c1, center_c2, center_c3 = st.columns([1, 6, 1])

    with center_c2:
        with st.container(border=True):
            st.markdown(
                """
                <div style="margin-bottom: 1.25rem;">
                    <span class="saas-badge-brand">Faculty Registration</span>
                    <h2 style="font-size:1.6rem; color:#0F172A; margin:0.35rem 0 0.15rem 0;">Create Faculty Account</h2>
                    <p style="color:#64748B; font-size:0.9rem; margin:0;">Register to start managing classes and running automated AI attendance.</p>
                </div>
                """,
                unsafe_allow_html=True
            )

            teacher_name = st.text_input("Full Name", placeholder='e.g. Prof. Ananya Roy', key="teacher_reg_name")
            teacher_username = st.text_input("Choose Username", placeholder='e.g. ananyaroy', key="teacher_reg_user")
            teacher_pass = st.text_input("Create Password", type='password', placeholder="••••••••", key="teacher_reg_pass")
            teacher_pass_confirm = st.text_input("Confirm Password", type='password', placeholder="••••••••", key="teacher_reg_confirm")

            st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

            btnc1, btnc2 = st.columns(2)
            with btnc1:
                if st.button('Complete Registration', type='primary', width='stretch'):
                    success, message = register_teacher(teacher_username, teacher_name, teacher_pass, teacher_pass_confirm)
                    if success:
                        st.success(message)
                        time.sleep(1.5)
                        st.session_state.teacher_login_type = "login"
                        st.rerun()
                    else:
                        st.error(message)

            with btnc2:
                if st.button('Sign In Instead', type="secondary", width='stretch'):
                    st.session_state.teacher_login_type = 'login'
                    st.rerun()

    footer_dashboard()