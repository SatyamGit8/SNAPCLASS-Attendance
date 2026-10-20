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

    # Default network Wi-Fi URL which works on all mobile phones on the same Wi-Fi
    default_wifi_url = f"http://{net_ip}:{port}/?join-code={subject_code}"
    localhost_url = f"http://localhost:8501/?join-code={subject_code}"

    link_type = st.radio(
        "Select QR Code Target:",
        options=["📱 Mobile / Wi-Fi (Scan with Phone)", "💻 Localhost", "🌐 Custom Deployed URL"],
        index=0,
        horizontal=True
    )

    if link_type == "📱 Mobile / Wi-Fi (Scan with Phone)":
        join_url = default_wifi_url
        st.caption(f"📶 Make sure the student's phone and this computer are connected to the same Wi-Fi network.")
    elif link_type == "💻 Localhost":
        join_url = localhost_url
    else:
        custom_domain = st.text_input(
            "Enter your deployed URL",
            placeholder="https://your-app-name.streamlit.app"
        )
        if custom_domain:
            domain = custom_domain.strip().rstrip('/')
            if not domain.startswith('http://') and not domain.startswith('https://'):
                domain = f"https://{domain}"
            join_url = f"{domain}/?join-code={subject_code}"
        else:
            join_url = default_wifi_url

    # Generate QR with error correction and high resolution
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
        st.success(f"🔑 **Class Code:** `{subject_code}`\n\nStudents already in SnapClass can simply click **'Enroll in Subject'** and type this code!")

    with col2:
        st.markdown('### 📷 Scan to Join')
        st.image(out.getvalue(), caption=f'QR Code ({subject_code})', use_container_width=True)
