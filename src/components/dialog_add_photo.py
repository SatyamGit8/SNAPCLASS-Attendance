import streamlit as st
from PIL import Image


@st.dialog("Add Classroom Group Photos")
def add_photos_dialog():
    st.markdown("### 📷 Add Classroom Photos")
    st.caption("Upload or capture high-resolution photos of your classroom. SnapClass will scan all student faces across all uploaded angles.")

    if 'attendance_images' not in st.session_state:
        st.session_state.attendance_images = []

    tabs = st.tabs(["📁 Upload Batch Photos", "📸 Live Camera Snapshot"])

    with tabs[0]:
        st.caption("Supported formats: JPG, JPEG, PNG. You can select multiple images covering different rows.")
        uploaded_files = st.file_uploader(
            "Upload classroom photos",
            type=['jpg', 'jpeg', 'png'],
            accept_multiple_files=True,
            key='uploader_classroom_photos'
        )

        if st.button("Add Photos to Queue", type="primary", disabled=not uploaded_files, width="stretch"):
            count = 0
            for f in uploaded_files:
                f.seek(0)
                img = Image.open(f).convert("RGB")
                st.session_state.attendance_images.append(img)
                count += 1
            st.toast(f"{count} photo(s) added to analysis queue!", icon="✅")
            st.rerun()

    with tabs[1]:
        st.caption("Take a snapshot directly from your webcam or laptop camera.")
        cam_photo = st.camera_input("Capture Classroom Snapshot", key="cam_classroom_snapshot")
        if cam_photo:
            if st.button("Add Snapshot to Queue", type="primary", width="stretch"):
                cam_photo.seek(0)
                img = Image.open(cam_photo).convert("RGB")
                st.session_state.attendance_images.append(img)
                st.toast("Snapshot added to queue!", icon="📸")
                st.rerun()

    st.markdown("<hr style='margin: 1rem 0;'>", unsafe_allow_html=True)
    current_count = len(st.session_state.attendance_images)
    st.caption(f"Queue Status: **{current_count}** photo(s) queued for AI Face Recognition.")

    if st.button("Close & View Photos", type="secondary", width="stretch"):
        st.rerun()
