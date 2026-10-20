import streamlit as st
import pandas as pd
from datetime import datetime
from src.pipelines.voice_pipeline import process_bulk_audio
from src.database.config import supabase
from src.components.dialog_attendance_results import show_attendance_result


@st.dialog('Voice Biometric Attendance')
def voice_attendance_dialog(selected_subject_id):
    st.markdown("### 🎙️ Record Classroom Roll Call")
    st.caption("Record continuous classroom audio of students saying *'Present'* or *'I am present'*. AI will isolate speech segments and match registered voice embeddings.")

    audio_data = st.audio_input("Record classroom audio roll call")

    st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

    if st.button('Analyze Audio Roll Call', width='stretch', type='primary'):
        if not audio_data:
            st.warning('Please record classroom audio before analyzing.')
            return

        with st.spinner('Processing audio streams & comparing speaker profiles...'):
            enrolled_res = supabase.table('subject_students').select("*, students(*)").eq('subject_id', selected_subject_id).execute()
            enrolled_students = enrolled_res.data or []

            if not enrolled_students:
                st.warning('No students are enrolled in this course.')
                return

            candidates_dict = {
                s['students']['student_id']: s['students']['voice_embedding']
                for s in enrolled_students if s.get('students') and s['students'].get('voice_embedding')
            }

            if not candidates_dict:
                st.error('None of the enrolled students in this course have voice profiles registered. Use Face Attendance instead.')
                return

            audio_bytes = audio_data.read()
            detected_scores = process_bulk_audio(audio_bytes, candidates_dict)

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
                    "Confidence": f"{round(score * 100, 1)}%" if is_present else "-",
                    "Status": "✅ Present" if is_present else "❌ Absent"
                })

                attendance_to_log.append({
                    'student_id': student['student_id'],
                    'subject_id': selected_subject_id,
                    'timestamp': current_timestamp,
                    'is_present': bool(is_present)
                })

            st.session_state.voice_attendance_results = (pd.DataFrame(results), attendance_to_log)

    if st.session_state.get('voice_attendance_results'):
        st.divider()
        df_results, logs = st.session_state.voice_attendance_results
        show_attendance_result(df_results, logs)
