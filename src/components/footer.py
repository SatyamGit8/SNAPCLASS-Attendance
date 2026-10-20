import streamlit as st


def footer_home():
    logo_url = "https://tse2.mm.bing.net/th/id/OIP.rnDT9E--GzURmXvkuDPYCAHaCm?r=0&rs=1&pid=ImgDetMain&o=7&rm=3"
    
    st.markdown(f"""
        <div style="margin-top:2rem; display:flex; gap:8px; justify-content:center; align-items:center">
            <p style="font-weight:bold; color:white; margin:0; font-size:0.95rem;"> Created with ❤️ by </p>  
            <div style="background:white; padding:3px 10px; border-radius:6px; display:inline-flex; align-items:center; box-shadow:0 2px 6px rgba(0,0,0,0.18);">
                <img src='{logo_url}' alt='SATYAM' style='height:20px; object-fit:contain;' />
            </div>
        </div>
    """, unsafe_allow_html=True)


def footer_dashboard():
    logo_url = "https://tse2.mm.bing.net/th/id/OIP.rnDT9E--GzURmXvkuDPYCAHaCm?r=0&rs=1&pid=ImgDetMain&o=7&rm=3"
    
    st.markdown(f"""
        <div style="margin-top:2rem; display:flex; gap:8px; justify-content:center; align-items:center">
            <p style="font-weight:bold; color:#1e293b; margin:0; font-size:0.95rem;"> Created with ❤️ by </p>  
            <img src='{logo_url}' alt='SATYAM' style='height:22px; object-fit:contain; vertical-align:middle;' />
        </div>
    """, unsafe_allow_html=True)
