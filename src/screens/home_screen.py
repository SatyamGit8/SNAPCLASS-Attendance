import streamlit as st
from src.components.header import header_home
from src.components.footer import footer_home
from src.ui.base_layout import style_base_layout, style_background_home


def home_screen():
    style_background_home()
    style_base_layout()

    header_home()

    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

    col1, col2 = st.columns(2, gap="large")

    with col1:
        with st.container(border=True):
            st.markdown(
                """
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:1rem;">
                    <span class="saas-badge-brand">🎓 Student Access</span>
                    <span style="font-size:0.8rem; color:#94A3B8; font-weight:500;">FaceID & Voice</span>
                </div>
                <h3 style="font-size:1.4rem; color:#0F172A; font-weight:700; margin-bottom:0.4rem;">Student Portal</h3>
                <p style="color:#64748B; font-size:0.925rem; line-height:1.5; min-height:48px;">
                    Sign in with FaceID to review your attendance statistics, subject enrollments, and lecture records.
                </p>
                <div style="margin: 1.25rem 0; padding: 0.85rem; background-color:#F8FAFC; border-radius:10px; border:1px solid #E2E8F0;">
                    <div style="display:flex; align-items:center; gap:8px; margin-bottom:6px; font-size:0.875rem; color:#334155;">
                        <span style="color:#10B981;">✓</span> 1-Click FaceID & Webcam Login
                    </div>
                    <div style="display:flex; align-items:center; gap:8px; margin-bottom:6px; font-size:0.875rem; color:#334155;">
                        <span style="color:#10B981;">✓</span> Self-Enrollment & Voice Profile
                    </div>
                    <div style="display:flex; align-items:center; gap:8px; font-size:0.875rem; color:#334155;">
                        <span style="color:#10B981;">✓</span> Enrolled Subjects & Live Stats
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
            if st.button('Enter Student Portal', type='primary', width='stretch', icon=':material/arrow_forward:'):
                st.session_state['login_type'] = 'student'
                st.rerun()

    with col2:
        with st.container(border=True):
            st.markdown(
                """
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:1rem;">
                    <span class="saas-badge-brand" style="background-color:#F5F3FF; color:#6D28D9; border-color:#DDD6FE;">👨‍🏫 Faculty Access</span>
                    <span style="font-size:0.8rem; color:#94A3B8; font-weight:500;">Educator Hub</span>
                </div>
                <h3 style="font-size:1.4rem; color:#0F172A; font-weight:700; margin-bottom:0.4rem;">Teacher Portal</h3>
                <p style="color:#64748B; font-size:0.925rem; line-height:1.5; min-height:48px;">
                    Take attendance with automated classroom group photos, run voice recognition, and manage course enrollments.
                </p>
                <div style="margin: 1.25rem 0; padding: 0.85rem; background-color:#F8FAFC; border-radius:10px; border:1px solid #E2E8F0;">
                    <div style="display:flex; align-items:center; gap:8px; margin-bottom:6px; font-size:0.875rem; color:#334155;">
                        <span style="color:#10B981;">✓</span> Multiple Classroom Photos Batch Scan
                    </div>
                    <div style="display:flex; align-items:center; gap:8px; margin-bottom:6px; font-size:0.875rem; color:#10B981;">
                        <span style="color:#10B981;">✓</span> AI Voice Recognition Attendance
                    </div>
                    <div style="display:flex; align-items:center; gap:8px; font-size:0.875rem; color:#334155;">
                        <span style="color:#10B981;">✓</span> Individual Student Presence Reports
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
            if st.button('Enter Teacher Portal', type='primary', width='stretch', icon=':material/arrow_forward:'):
                st.session_state['login_type'] = 'teacher'
                st.rerun()

    footer_home()