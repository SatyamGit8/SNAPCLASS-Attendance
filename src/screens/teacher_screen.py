import streamlit as st

from src.ui.base_layout import style_background_dashboard, style_base_layout

from src.components.header import header_dashboard
from src.components.footer import footer_dashboard
from src.components.subject_card import subject_card
from src.database.db import check_teacher_exists, create_teacher, teacher_login, get_teacher_subjects, get_attendance_for_teacher
from src.components.dialog_create_subject import create_subject_dialog
from src.components.dialog_share_subject import share_subject_dialog
from src.components.dialog_add_photo import add_photos_dialog

from src.pipelines.face_pipeline import predict_attendance
from src.components.dialog_attendance_results import attendance_result_dialog
import numpy as np

from datetime import datetime

import pandas as pd

from src.database.config import supabase


from src.components.dialog_voice_attendance import voice_attendance_dialog
from src.pipelines.voice_pipeline import process_bulk_audio
from PIL import Image

def teacher_screen():

    style_background_dashboard()
    style_base_layout()

    if "teacher_data" in st.session_state:
        teacher_dashboard()
    elif 'teacher_login_type' not in st.session_state or st.session_state.teacher_login_type=="login":
        teacher_screen_login()
    elif st.session_state.teacher_login_type == "register":
        teacher_screen_register()





def teacher_dashboard():
    teacher_data = st.session_state.teacher_data
    c1, c2 = st.columns(2, vertical_alignment='center', gap='xxlarge')
    with c1:
        header_dashboard()
    with c2:
        st.subheader(f"""Welcome, {teacher_data['name']} """)
        if st.button("Logout", type='secondary', key='loginbackbtn', shortcut="control+backspace"):
            st.session_state['is_logged_in'] = False
            del st.session_state.teacher_data 
            st.rerun()


    st.space()

    if "current_teacher_tab" not in st.session_state:
        st.session_state.current_teacher_tab = 'take_attendance'
    tab1, tab2, tab3 = st.columns(3)


    with tab1:
        type1 = "primary" if st.session_state.current_teacher_tab == 'take_attendance' else "tertiary"
        if st.button('Take Attendance',type=type1, width='stretch', icon=':material/ar_on_you:'):
            st.session_state.current_teacher_tab = 'take_attendance'
            st.rerun()

    with tab2:
        type2 = "primary" if st.session_state.current_teacher_tab == 'manage_subjects' else "tertiary"
        if st.button('Manage Subjects', type=type2, width='stretch', icon=':material/book_ribbon:'):
            st.session_state.current_teacher_tab = 'manage_subjects'
            st.rerun()

    with tab3:
        type3 = "primary" if st.session_state.current_teacher_tab == 'attendance_records' else "tertiary"
        if st.button('Attendance Records',type=type3, width='stretch', icon=':material/cards_stack:'):
            st.session_state.current_teacher_tab = 'attendance_records'
            st.rerun()


    st.divider()

    if st.session_state.current_teacher_tab == "take_attendance":
        teacher_tab_take_attendance()
    if st.session_state.current_teacher_tab == "manage_subjects":
        teacher_tab_manage_subjects()
    if st.session_state.current_teacher_tab == "attendance_records":
        teacher_tab_attendance_records()

    


    footer_dashboard()

def teacher_tab_take_attendance():
    teacher_id = st.session_state.teacher_data['teacher_id']
    st.header('Take AI Attendance')

    subjects = get_teacher_subjects(teacher_id)

    if not subjects:
        st.warning('You haven\'t created any subjects yet! Please create one in Manage Subjects to begin!')
        return

    subject_options = {f"{s['name']} - {s['subject_code']}": s['subject_id'] for s in subjects}
    selected_subject_label = st.selectbox('Select Subject', options=list(subject_options.keys()))
    selected_subject_id = subject_options[selected_subject_label]

    enrolled_res = supabase.table('subject_students').select("*, students(*)").eq('subject_id', selected_subject_id).execute()
    enrolled_students = enrolled_res.data or []

    st.caption(f"👥 **Enrolled Students:** {len(enrolled_students)} student(s) currently enrolled in this subject.")
    if not enrolled_students:
        st.info("💡 **Tip:** No students are enrolled yet in this subject. Students can enroll via the **Student Portal** using the Subject Code!")

    st.space()

    # Three Attendance Modes: Face ID, Voice, or Combined (Dual)
    att_tab_face, att_tab_voice, att_tab_dual = st.tabs([
        "📸 Face ID Attendance",
        "🎙️ Voice Attendance",
        "⚡ Combined (Face + Voice)"
    ])

    # ================= TAB 1: FACE ID ATTENDANCE =================
    with att_tab_face:
        st.subheader("Face Recognition Attendance")
        st.caption("Upload classroom photos or capture a live webcam photo to recognize and mark all students present.")

        f_col1, f_col2 = st.columns(2)
        with f_col1:
            face_uploaded_files = st.file_uploader(
                "Upload classroom photo(s)",
                type=['jpg', 'jpeg', 'png'],
                accept_multiple_files=True,
                key="teacher_face_upload"
            )
        with f_col2:
            st.caption("Or capture directly from classroom webcam:")
            face_cam_file = st.camera_input("Take Live Classroom Photo", key="teacher_face_cam")

        all_face_images = []
        if face_uploaded_files:
            for f in face_uploaded_files:
                f.seek(0)
                all_face_images.append(Image.open(f).convert("RGB"))
        if face_cam_file:
            face_cam_file.seek(0)
            all_face_images.append(Image.open(face_cam_file).convert("RGB"))

        if all_face_images:
            st.info(f"📊 **{len(all_face_images)}** photo(s) ready for Face Analysis.")
            preview_cols = st.columns(min(len(all_face_images), 4))
            for p_idx, p_img in enumerate(all_face_images[:4]):
                with preview_cols[p_idx]:
                    st.image(p_img, caption=f"Photo {p_idx+1}", width="stretch")

        if st.button("🔍 Run Face Analysis & Mark Attendance", type="primary", width="stretch", disabled=not all_face_images):
            if not enrolled_students:
                st.warning("No students are enrolled in this course yet.")
            else:
                with st.spinner("Scanning classroom photo(s) for student faces..."):
                    all_detected_ids = {}
                    total_faces_found = 0

                    for idx, img in enumerate(all_face_images):
                        img_np = np.array(img)
                        detected, _, num_faces = predict_attendance(img_np, tolerance=0.58)
                        total_faces_found += num_faces

                        if detected:
                            for sid in detected.keys():
                                all_detected_ids.setdefault(int(sid), []).append(f"Photo {idx+1}")

                    if total_faces_found == 0:
                        st.warning("⚠️ No faces detected in the provided photo(s). Please ensure faces are clearly lit and facing the camera.")
                    else:
                        st.toast(f"Detected {total_faces_found} face(s) across photos!", icon="📸")

                    results, attendance_to_log = [], []
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
                            "Source": ", ".join(sources) if is_present else "-",
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

    # ================= TAB 2: VOICE ATTENDANCE =================
    with att_tab_voice:
        st.subheader("Voice Recognition Attendance")
        st.caption("Record classroom audio of students answering roll call / speaking. AI will recognize enrolled voices.")

        voice_audio = st.audio_input("Record classroom audio", key="teacher_voice_audio")

        if st.button("🎙️ Analyze Voice & Mark Attendance", type="primary", width="stretch", disabled=not voice_audio):
            if not enrolled_students:
                st.warning("No students enrolled in this course yet.")
            else:
                candidates_dict = {
                    s['students']['student_id']: s['students']['voice_embedding']
                    for s in enrolled_students if s.get('students') and s['students'].get('voice_embedding')
                }
                if not candidates_dict:
                    st.error("None of the enrolled students have voice profiles registered yet.")
                else:
                    with st.spinner("Analyzing classroom voice audio..."):
                        voice_audio.seek(0)
                        detected_scores = process_bulk_audio(voice_audio.read(), candidates_dict)

                        results, attendance_to_log = [], []
                        current_timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

                        for node in enrolled_students:
                            student = node.get('students')
                            if not student:
                                continue
                            score = detected_scores.get(student['student_id'], 0.0)
                            is_present = bool(score > 0)

                            results.append({
                                "Name": student['name'],
                                "ID": student['student_id'],
                                "Source": "Voice" if is_present else "-",
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

    # ================= TAB 3: DUAL ATTENDANCE (FACE + VOICE) =================
    with att_tab_dual:
        st.subheader("⚡ Combined Attendance (Face + Voice)")
        st.caption("Take classroom photo(s) AND record audio in one session. Students recognized by EITHER Face OR Voice will be marked Present!")

        d_col1, d_col2 = st.columns(2)
        with d_col1:
            st.markdown("##### 📸 Step 1: Classroom Photo")
            dual_photo_upload = st.file_uploader(
                "Upload classroom photo",
                type=['jpg', 'jpeg', 'png'],
                key="dual_att_photo"
            )
            dual_cam_photo = st.camera_input("Or take live snapshot", key="dual_att_cam")
            dual_photo = dual_photo_upload if dual_photo_upload is not None else dual_cam_photo

        with d_col2:
            st.markdown("##### 🎙️ Step 2: Classroom Audio")
            dual_audio = st.audio_input("Record classroom audio / roll call", key="dual_att_audio")

        dual_ready = (dual_photo is not None) or (dual_audio is not None)

        if st.button("⚡ Run Combined AI Attendance", type="primary", width="stretch", disabled=not dual_ready):
            if not enrolled_students:
                st.warning("No students enrolled in this course yet.")
            else:
                with st.spinner("Running Multi-Modal AI Attendance (Face + Voice)..."):
                    # 1. Face Analysis
                    face_detected_ids = set()
                    if dual_photo:
                        dual_photo.seek(0)
                        d_img_np = np.array(Image.open(dual_photo).convert("RGB"))
                        d_detected, _, num_faces = predict_attendance(d_img_np, tolerance=0.58)
                        if d_detected:
                            face_detected_ids = {int(sid) for sid in d_detected.keys()}

                    # 2. Voice Analysis
                    voice_detected_ids = set()
                    if dual_audio:
                        dual_audio.seek(0)
                        candidates_dict = {
                            s['students']['student_id']: s['students']['voice_embedding']
                            for s in enrolled_students if s.get('students') and s['students'].get('voice_embedding')
                        }
                        if candidates_dict:
                            v_scores = process_bulk_audio(dual_audio.read(), candidates_dict)
                            voice_detected_ids = {sid for sid, score in v_scores.items() if score > 0}

                    # 3. Combine Results
                    results, attendance_to_log = [], []
                    current_timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

                    for node in enrolled_students:
                        student = node.get('students')
                        if not student:
                            continue
                        sid = int(student['student_id'])
                        by_face = sid in face_detected_ids
                        by_voice = sid in voice_detected_ids
                        is_present = by_face or by_voice

                        if by_face and by_voice:
                            source_tag = "FaceID + Voice"
                        elif by_face:
                            source_tag = "FaceID"
                        elif by_voice:
                            source_tag = "Voice"
                        else:
                            source_tag = "-"

                        results.append({
                            "Name": student['name'],
                            "ID": student['student_id'],
                            "Source": source_tag,
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











def teacher_tab_manage_subjects():
    teacher_id = st.session_state.teacher_data['teacher_id']
    col1, col2 = st.columns(2)
    with col1:
        st.header('Manage Subjects', width='stretch')

    with col2:
        if st.button('Create New Subject', width='stretch'):
            create_subject_dialog(teacher_id)


    # LIST all SUBJECTS
    subjects = get_teacher_subjects(teacher_id)
    if subjects:
        for sub in subjects:
            stats = [
                ("🫂", "Students", sub['total_students']),
                ("🕰️", "Classes", sub['total_classes']),
            ]
        def share_btn():
            if st.button(f"Share Code: {sub['name']}", key=f"share_{sub['subject_code']}", icon=":material/share:"):
                share_subject_dialog(sub['name'], sub['subject_code'])
            st.space()

        subject_card(
            name = sub['name'],
            code = sub['subject_code'],
            section = sub['section'],
            stats=stats,
            footer_callback=share_btn
        )
    else:
        st.info("NO SUBJECTS FOUND. CREATE ONE ABOVE")


def teacher_tab_attendance_records():
    st.header('Attendance Records')

    teacher_id = st.session_state.teacher_data['teacher_id']

    records = get_attendance_for_teacher(teacher_id)

    if not records:
        st.info("No attendance records found yet. Take attendance using face or voice to see records here.")
        return
    
    data = []

    for r in records:
        ts = r.get('timestamp')
        student = r.get('students') or {}

        data.append({
            "ts_group": ts.split(".")[0] if ts else None,
            "Time": datetime.fromisoformat(ts).strftime("%Y-%m-%d %I:%M %p") if ts else "N/A",
            "Subject": r['subjects']['name'],
            "Subject Code": r['subjects']['subject_code'],
            "Student Name": student.get('name', f"Student #{r.get('student_id')}"),
            "Student ID": r.get('student_id'),
            "is_present": bool(r.get('is_present', False)),
            "Status": "✅ Present" if r.get('is_present', False) else "❌ Absent"
        })

    df = pd.DataFrame(data)

    st.subheader("📋 Session Summary")
    summary = (
        df.groupby(['ts_group', 'Time', 'Subject', 'Subject Code'])
        .agg(
            Present_Count = ('is_present', 'sum'),
            Total_Count =('is_present', 'count')
        ).reset_index()
    )

    summary['Attendance Stats'] = (
        "✅ " + summary['Present_Count'].astype(str) + " / "
        + summary['Total_Count'].astype(str) + ' Present'
    )

    display_df = ( summary.sort_values(by='ts_group', ascending=False)
                  [['Time', 'Subject', 'Subject Code', 'Attendance Stats']]
                  )
    
    st.dataframe(display_df, width='stretch', hide_index=True)

    st.divider()

    st.subheader("🔍 Detailed Student List by Session")
    st.caption("Select an attendance session below to see individual students who were marked Present or Absent.")

    sessions = summary.sort_values(by='ts_group', ascending=False)
    session_options = {
        f"{row['Time']} — {row['Subject']} ({row['Subject Code']})": row['ts_group']
        for _, row in sessions.iterrows()
    }

    if session_options:
        selected_session_label = st.selectbox("Select Session", options=list(session_options.keys()))
        selected_ts = session_options[selected_session_label]

        session_students = df[df['ts_group'] == selected_ts][['Student Name', 'Student ID', 'Status', 'Time']]
        
        c1, c2 = st.columns([1, 3])
        with c1:
            filter_choice = st.radio("Filter", ["All", "Present Only", "Absent Only"], horizontal=True)

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
        st.session_state.user_role ='teacher'
        st.session_state.teacher_data = teacher
        st.session_state.is_logged_in = True
        return True
    

    return False
def teacher_screen_login():
    c1, c2 = st.columns(2, vertical_alignment='center', gap='xxlarge')
    with c1:
        header_dashboard()
    with c2:
        if st.button("Go back to Home", type='secondary', key='loginbackbtn', shortcut="control+backspace"):
            st.session_state['login_type'] = None
            st.rerun()

    st.header('Login using password', text_alignment='center')
    st.space()
    st.space()


    teacher_username = st.text_input("Enter username", placeholder='ananyaroy')

    teacher_pass = st.text_input("Enter password", type='password', placeholder="Enter password")

    st.divider()

    btnc1, btnc2 = st.columns(2)

    with btnc1:
        if st.button('Login', icon=':material/passkey:', shortcut='control+enter', width='stretch'):
            if login_teacher(teacher_username, teacher_pass):
                st.toast("welcome back!", icon="👋")
                import time
                time.sleep(1)
                st.rerun()
            else:
                st.error("Invalid username and password combo")

    with btnc2:
        if st.button('Register Instead', type="primary", icon=':material/passkey:', width='stretch'):
            st.session_state.teacher_login_type = 'register'

    footer_dashboard()



def register_teacher(teacher_username, teacher_name, teacher_pass, teacher_pass_confirm):
    if not teacher_username or not teacher_name or not teacher_pass:
        return False, "All Fields are required!"
    if check_teacher_exists(teacher_username):
        return False, "Username already taken"
    if teacher_pass != teacher_pass_confirm:
        return False, "Password doesn't match"
    
    try:
        res = create_teacher(teacher_username, teacher_pass, teacher_name)
        if res:
            return True, "Successfully Created! Login Now"
        return False, "Failed to create account. Please check database permissions or try again."
    except Exception as e:
        return False, f"Unexpected Error: {e}"
    

def teacher_screen_register():
    c1, c2 = st.columns(2, vertical_alignment='center', gap='xxlarge')
    with c1:
        header_dashboard()
    with c2:
        if st.button("Go back to Home", type='secondary', key='loginbackbtn', shortcut="control+backspace"):
            st.session_state['login_type'] = None
            st.rerun()



    st.header('Register your teacher profile')

    st.space()
    st.space()

    
    teacher_username = st.text_input("Enter username", placeholder='ananyaroy')

    teacher_name = st.text_input("Enter name", placeholder='Ananya Roy')

    teacher_pass = st.text_input("Enter password", type='password', placeholder="Enter password")

    teacher_pass_confirm = st.text_input("Confirm your password", type='password', placeholder="Enter password")

    st.divider()

    btnc1, btnc2 = st.columns(2)

    with btnc1:
        if st.button('Register now', icon=':material/passkey:', shortcut='control+enter', width='stretch'):
            success, message = register_teacher(teacher_username, teacher_name, teacher_pass, teacher_pass_confirm)
            if success:
                st.success(message)
                import time
                time.sleep(2)
                st.session_state.teacher_login_type = "login"
                st.rerun()
            else:
                st.error(message)


    with btnc2:
        if st.button('Login Instead', type="primary", icon=':material/passkey:', width='stretch'):
            st.session_state.teacher_login_type = 'login'

    footer_dashboard()