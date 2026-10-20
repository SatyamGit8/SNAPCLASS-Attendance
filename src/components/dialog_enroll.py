import streamlit as st
import time
from src.database.db import enroll_student_to_subject
from src.database.config import supabase


@st.dialog("Enroll in Course")
def enroll_dialog():
    st.caption("Enter the unique course code provided by your instructor to register:")
    join_code = st.text_input('Course Code', placeholder='e.g. ECS-403 or CS101')

    st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

    if st.button('Enroll Now', type='primary', width='stretch'):
        clean_code = join_code.strip() if join_code else ""
        if clean_code:
            res = supabase.table('subjects').select('subject_id, name, subject_code').ilike('subject_code', clean_code).execute()
            if res.data:
                subject = res.data[0]
                student_id = st.session_state.student_data['student_id']

                check = supabase.table('subject_students').select('*').eq('subject_id', subject['subject_id']).eq('student_id', student_id).execute()
                if check.data:
                    st.warning('You are already enrolled in this course!')
                else:
                    enroll_student_to_subject(student_id, subject['subject_id'])
                    st.toast(f'Successfully enrolled in {subject["name"]}!', icon="🎉")
                    time.sleep(1)
                    st.rerun()
            else:
                st.error(f'Course code "{clean_code}" was not found. Please verify with your instructor.')
        else:
            st.warning('Please enter a valid course code.')