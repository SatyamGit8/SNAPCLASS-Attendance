import streamlit as st
import segno
import io
import socket


def get_network_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(0.5)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        try:
            return socket.gethostbyname(socket.gethostname())
        except Exception:
            return "localhost"


@st.dialog("Share Class Link & QR Code")
def share_subject_dialog(subject_name, subject_code):
    net_ip = get_network_ip()
    port = "8501"

    options = {
        f"📱 Mobile / Wi-Fi (http://{net_ip}:{port})": f"http://{net_ip}:{port}/?join-code={subject_code}",
        "☁️ Cloud / Production (https://snapclass-main.streamlit.app)": f"https://snapclass-main.streamlit.app/?join-code={subject_code}",
        "💻 Localhost (http://localhost:8501)": f"http://localhost:8501/?join-code={subject_code}",
    }

    selected_option = st.selectbox(
        "Select QR Link Target:",
        options=list(options.keys()),
        index=0,
        help="Choose 'Mobile / Wi-Fi' if scanning with a phone on the same Wi-Fi network, or 'Cloud' if deployed online."
    )
    join_url = options[selected_option]

    qr = segno.make(join_url, error='m')
    out = io.BytesIO()
    qr.save(out, kind='png', scale=8, border=2)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown('### 📋 Join Details')
        st.markdown(f"**Course:** {subject_name}")
        st.markdown(f"**Class Code:** `{subject_code}`")
        st.caption("Direct Join URL:")
        st.code(join_url, language="text")
        st.info("💡 **How it works:**\n- Scan the QR code using any phone camera to open SnapClass and auto-join.\n- Or enter the Class Code manually in the Student Dashboard.")

    with col2:
        st.markdown('### 📷 Scan to Join')
        st.image(out.getvalue(), caption=f'QR Code for {subject_code}', use_container_width=True)
