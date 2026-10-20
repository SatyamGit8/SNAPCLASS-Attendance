import streamlit as st


def footer_home():
    logo_url = "https://i.ibb.co/4r5X1FY/apnacollege.png"

    st.markdown(
        f"""
        <div style="margin-top:4rem; padding-top:1.5rem; border-top:1px solid #E2E8F0; display:flex; align-items:center; justify-content:center; gap:8px;">
            <span style="font-size:0.875rem; color:#64748B; font-weight:500;">Powered by</span>
            <img src='{logo_url}' style='height:20px; object-fit:contain;' alt='Apna College' />
            <span style="font-size:0.875rem; color:#94A3B8;">•</span>
            <span style="font-size:0.875rem; color:#64748B;">Secure Biometric Attendance</span>
        </div>
        """,
        unsafe_allow_html=True
    )


def footer_dashboard():
    logo_url = "https://i.ibb.co/4r5X1FY/apnacollege.png"

    st.markdown(
        f"""
        <div style="margin-top:3rem; padding-top:1.25rem; border-top:1px solid #E2E8F0; display:flex; align-items:center; justify-content:center; gap:8px;">
            <span style="font-size:0.825rem; color:#64748B; font-weight:500;">Powered by</span>
            <img src='{logo_url}' style='height:18px; object-fit:contain;' alt='Apna College' />
            <span style="font-size:0.825rem; color:#94A3B8;">•</span>
            <span style="font-size:0.825rem; color:#64748B;">SnapClass SaaS</span>
        </div>
        """,
        unsafe_allow_html=True
    )
