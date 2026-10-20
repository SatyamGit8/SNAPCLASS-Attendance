import streamlit as st
from PIL import Image


@st.dialog("Add Classroom Group Photos")
def add_photos_dialog():
    st.write("📷 **Upload or capture multiple classroom group photos** to automatically recognize all students.")

    if 'attendance_images' not in st.session_state:
        st.session_state.attendance_images = []

    tabs = st.tabs(["📁 Upload Multiple Group Photos", "📸 Live Camera Snapshot"])

    with tabs[0]:
        st.caption("Upload one or multiple photos covering different angles/rows of your classroom.")
        uploaded_files = st.file_uploader(
            "Select classroom group photo(s)",
            type=['jpg', 'jpeg', 'png'],
            accept_multiple_files=True,
            key='uploader_classroom_photos'
        )

        if st.button("➕ Add Photos to Analysis Batch", type="primary", disabled=not uploaded_files, width="stretch"):
            count = 0
            for f in uploaded_files:
                f.seek(0)
                img = Image.open(f).convert("RGB")
                st.session_state.attendance_images.append(img)
                count += 1
            st.toast(f"{count} classroom photo(s) added successfully!", icon="✅")
            st.rerun()

    with tabs[1]:
        st.caption("Capture a live snapshot of the classroom from your device camera.")
        cam_photo = st.camera_input("Capture Classroom Photo", key="cam_classroom_snapshot")
        if cam_photo:
            if st.button("➕ Add This Snapshot", type="primary", width="stretch"):
                cam_photo.seek(0)
                img = Image.open(cam_photo).convert("RGB")
                st.session_state.attendance_images.append(img)
                st.toast("Snapshot added to batch!", icon="📸")
                st.rerun()

    st.divider()
    current_count = len(st.session_state.attendance_images)
    st.info(f"📊 Currently **{current_count}** photo(s) ready for AI Face Analysis.")

    if st.button("Done", type="secondary", width="stretch"):
        st.rerun()
