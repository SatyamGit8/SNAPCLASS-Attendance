import streamlit as st
import pandas as pd
from src.database.db import create_attendance


def show_attendance_result(df: pd.DataFrame, logs: list):
    st.markdown("### 📊 AI Attendance Recognition Summary")
    st.caption("Review detected students below and confirm to record this session in the database.")

    total = len(df)
    present_count = len(df[df['Status'].str.contains('Present', na=False)])
    absent_count = total - present_count
    pct = round((present_count / total * 100), 1) if total > 0 else 0.0

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Enrolled", total)
    m2.metric("Present", present_count)
    m3.metric("Absent", absent_count)
    m4.metric("Turnout", f"{pct}%")

    st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
    st.dataframe(df, hide_index=True, width='stretch')

    st.markdown("<hr style='margin: 1rem 0;'>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        if st.button('Discard Results', type='secondary', width='stretch'):
            st.session_state.voice_attendance_results = None
            st.session_state.attendance_images = []
            st.rerun()

    with col2:
        if st.button('✅ Confirm & Save Attendance', width='stretch', type='primary'):
            try:
                create_attendance(logs)
                st.toast("Attendance successfully recorded in database!", icon="🎉")
                st.session_state.attendance_images = []
                st.session_state.voice_attendance_results = None
                st.rerun()
            except Exception as e:
                st.error(f'Sync failed: {e}')


@st.dialog("Attendance Results & Confirmation")
def attendance_result_dialog(df, logs):
    show_attendance_result(df, logs)
