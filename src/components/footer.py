import streamlit as st


def footer_home():
    st.markdown("""
        <div style="margin-top:2rem; display:flex; justify-content:center; align-items:center;">
            <p style="font-weight:bold; color:white; font-size:1.05rem; margin:0; letter-spacing:0.5px; font-family:'Outfit', sans-serif;">
                Created with ❤️ by <span style="font-weight:800; letter-spacing:1px; text-transform:uppercase;">SATYAM</span>
            </p>
        </div>
    """, unsafe_allow_html=True)


def footer_dashboard():
    st.markdown("""
        <div style="margin-top:2rem; display:flex; justify-content:center; align-items:center;">
            <p style="font-weight:bold; color:#1e293b; font-size:1.05rem; margin:0; letter-spacing:0.5px; font-family:'Outfit', sans-serif;">
                Created with ❤️ by <span style="font-weight:800; letter-spacing:1px; color:#5865F2; text-transform:uppercase;">SATYAM</span>
            </p>
        </div>
    """, unsafe_allow_html=True)
