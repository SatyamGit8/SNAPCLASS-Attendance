import streamlit as st
from src.database.db import create_subject


@st.dialog("Create New Course")
def create_subject_dialog(teacher_id):
    st.caption("Fill in the course details below to generate a unique enrollment code.")

    sub_id = st.text_input("Course / Subject Code", placeholder="e.g. CS101 or ECS-403")
    sub_name = st.text_input("Course Name", placeholder="e.g. Introduction to Machine Learning")
    sub_section = st.text_input("Class Section", placeholder="e.g. A, B, or Morning")

    st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

    if st.button("Create Course", type='primary', width='stretch'):
        if sub_id.strip() and sub_name.strip() and sub_section.strip():
            try:
                create_subject(sub_id.strip(), sub_name.strip(), sub_section.strip(), teacher_id)
                st.toast("Course created successfully!", icon="🎉")
                st.rerun()
            except Exception as e:
                st.error(f"Error creating course: {str(e)}")
        else:
            st.warning("Please fill in all course fields.")
