import streamlit as st


def header_home():
    logo_url = "https://i.ibb.co/YTYGn5qV/logo.png"

    st.markdown(
        f"""
        <div style="display:flex; flex-direction:column; align-items:center; justify-content:center; padding: 1.5rem 0 2rem 0;">
            <div style="display:flex; align-items:center; gap: 12px; margin-bottom: 0.75rem;">
                <img src='{logo_url}' style='height:48px; width:48px; object-fit:contain;' />
                <span style="font-family:'Plus Jakarta Sans', sans-serif; font-size:1.85rem; font-weight:800; color:#0F172A; letter-spacing:-0.03em;">
                    Snap<span style="color:#2563EB;">Class</span>
                </span>
                <span class="saas-badge-brand" style="margin-left:6px;">Smart AI Attendance</span>
            </div>
            <h1 style="text-align:center; font-size:2.4rem; color:#0F172A; font-weight:800; max-width:700px; margin:0.25rem auto;">
                Next-Gen Classroom Attendance System
            </h1>
            <p style="text-align:center; color:#64748B; font-size:1.05rem; max-width:620px; line-height:1.5; margin:0.5rem auto 0 auto;">
                Automated facial recognition and voice verification for students and educators. Fast, reliable, and effortless.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )


def header_dashboard():
    logo_url = "https://i.ibb.co/YTYGn5qV/logo.png"

    st.markdown(
        f"""
        <div style="display:flex; align-items:center; gap: 10px; padding: 0.25rem 0;">
            <img src='{logo_url}' style='height:40px; width:40px; object-fit:contain;' />
            <div style="display:flex; flex-direction:column;">
                <span style="font-family:'Plus Jakarta Sans', sans-serif; font-size:1.35rem; font-weight:800; color:#0F172A; letter-spacing:-0.03em; line-height:1.1;">
                    Snap<span style="color:#2563EB;">Class</span>
                </span>
                <span style="font-size:0.75rem; color:#64748B; font-weight:500;">AI Attendance Platform</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
