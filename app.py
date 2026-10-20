import sys
import os
import types

# Ensure pkg_resources is available for face_recognition_models and webrtcvad on environments without setuptools
try:
    import pkg_resources
except ImportError:
    pkg_resources = types.ModuleType("pkg_resources")
    sys.modules["pkg_resources"] = pkg_resources

if not hasattr(pkg_resources, "resource_filename"):
    def _resource_filename(package_or_requirement, resource_name):
        import importlib.util
        pkg_name = package_or_requirement if isinstance(package_or_requirement, str) else getattr(package_or_requirement, "__name__", str(package_or_requirement))
        try:
            spec = importlib.util.find_spec(pkg_name)
            if spec and spec.origin:
                pkg_dir = os.path.dirname(spec.origin)
                return os.path.join(pkg_dir, resource_name)
        except Exception:
            pass
        return resource_name
    pkg_resources.resource_filename = _resource_filename

if not hasattr(pkg_resources, "get_distribution"):
    class _DummyDistribution:
        def __init__(self, name="pkg"):
            self.version = "2.0.10"
            self.project_name = name
    def _get_distribution(dist_name):
        return _DummyDistribution(dist_name)
    pkg_resources.get_distribution = _get_distribution

import streamlit as st

from src.screens.home_screen import home_screen
from src.screens.teacher_screen import teacher_screen
from src.screens.student_screen import student_screen

from src.components.dialog_auto_enroll import auto_enroll_dialog


def main():
    st.set_page_config(
        page_title='SnapClass — Smart AI Attendance Platform',
        page_icon="https://i.ibb.co/YTYGn5qV/logo.png",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    if 'login_type' not in st.session_state:
        st.session_state['login_type'] = None

    match st.session_state['login_type']:
        case 'teacher':
            teacher_screen()

        case 'student':
            student_screen()

        case None:
            home_screen()

    # Handle QR Code / Link join-code query param
    join_code = st.query_params.get('join-code') or st.session_state.get('pending_join_code')
    if join_code:
        st.session_state['pending_join_code'] = join_code

        if st.session_state.get('is_logged_in') and st.session_state.get('user_role') == 'student':
            auto_enroll_dialog(join_code)
        elif st.session_state.get('is_logged_in') and st.session_state.get('user_role') == 'teacher':
            st.info(f"Class join link received for **{join_code}**. Please log in with a student account to enroll.")
        else:
            if st.session_state.get('login_type') != 'student':
                st.session_state['login_type'] = 'student'
                st.rerun()


main()