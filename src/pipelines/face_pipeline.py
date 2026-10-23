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

from PIL import Image, ImageOps
import dlib
import numpy as np
import face_recognition_models
import streamlit as st
from src.database.db import get_all_students


def load_and_orient_image(file_or_bytes_or_img, max_dim=1280):
    """
    Safely loads an image file/stream/bytes/Image, automatically corrects smartphone
    EXIF orientation (portrait vs landscape), downscales huge phone photos,
    and returns a clean, C-contiguous RGB numpy array.
    """
    if isinstance(file_or_bytes_or_img, np.ndarray):
        img_np = file_or_bytes_or_img
        if img_np.ndim == 2:
            img_np = np.stack([img_np] * 3, axis=-1)
        elif img_np.shape[2] == 4:
            img_np = img_np[:, :, :3]
        return np.ascontiguousarray(img_np, dtype=np.uint8)

    if isinstance(file_or_bytes_or_img, Image.Image):
        img = file_or_bytes_or_img
    else:
        if hasattr(file_or_bytes_or_img, 'seek'):
            file_or_bytes_or_img.seek(0)
        img = Image.open(file_or_bytes_or_img)

    # 1. Correct smartphone EXIF rotation (fixes sideways/upside-down phone photos)
    try:
        img = ImageOps.exif_transpose(img)
    except Exception:
        pass

    img = img.convert('RGB')

    # 2. Downscale huge phone images to prevent slow detection / memory issues
    w, h = img.size
    if max(w, h) > max_dim:
        scale = max_dim / max(w, h)
        new_w, new_h = max(1, int(w * scale)), max(1, int(h * scale))
        img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)

    return np.ascontiguousarray(np.array(img), dtype=np.uint8)


@st.cache_resource
def load_dlib_models():
    detector = dlib.get_frontal_face_detector()

    sp = dlib.shape_predictor(
        face_recognition_models.pose_predictor_model_location()
    )

    facerec = dlib.face_recognition_model_v1(
        face_recognition_models.face_recognition_model_location()
    )

    return detector, sp, facerec


def get_face_embeddings(image_np):
    """
    Detects faces and computes 128-d face descriptors.
    Includes automatic multi-orientation fallback (0°, 90°, 270°, 180°)
    to guarantee phone camera selfies taken sideways are properly recognized.
    """
    detector, sp, facerec = load_dlib_models()

    if not isinstance(image_np, np.ndarray):
        image_np = load_and_orient_image(image_np)
    elif not image_np.flags['C_CONTIGUOUS']:
        image_np = np.ascontiguousarray(image_np)

    working_img = image_np
    faces = detector(working_img, 1)
    if len(faces) == 0:
        faces = detector(working_img, 2)

    # If no face found in default orientation, test other rotations (common on smartphones)
    if len(faces) == 0:
        for k in [1, 3, 2]:
            rotated = np.ascontiguousarray(np.rot90(image_np, k))
            r_faces = detector(rotated, 1)
            if len(r_faces) == 0:
                r_faces = detector(rotated, 2)
            if len(r_faces) > 0:
                faces = r_faces
                working_img = rotated
                break

    encodings = []
    for face in faces:
        shape = sp(working_img, face)
        # Using 2 jitters for slightly perturbing & averaging descriptor (stabilizes tilted/angled poses)
        face_descriptor = facerec.compute_face_descriptor(working_img, shape, 2)
        encodings.append(np.array(face_descriptor, dtype=np.float64))
    return encodings


@st.cache_resource(ttl=5)
def get_trained_model():
    X = []
    y = []

    student_db = get_all_students()
    if not student_db:
        return None

    for student in student_db:
        embedding = student.get('face_embedding')
        sid = student.get('student_id')
        if embedding is not None and sid is not None:
            emb_arr = np.array(embedding, dtype=np.float64)
            int_sid = int(sid)
            # Case 1: Standard single 128-d vector
            if emb_arr.ndim == 1 and len(emb_arr) == 128:
                X.append(emb_arr)
                y.append(int_sid)
            # Case 2: Multi-embedding concatenated array (128 * N)
            elif emb_arr.ndim == 1 and len(emb_arr) >= 128 and len(emb_arr) % 128 == 0:
                num_sub = len(emb_arr) // 128
                for k in range(num_sub):
                    X.append(emb_arr[k*128:(k+1)*128])
                    y.append(int_sid)
            # Case 3: 2D array (N, 128)
            elif emb_arr.ndim == 2 and emb_arr.shape[1] == 128:
                for single_emb in emb_arr:
                    X.append(single_emb)
                    y.append(int_sid)

    if len(X) == 0:
        return None

    return {'X': X, 'y': y}


def train_classifier():
    st.cache_resource.clear()
    model_data = get_trained_model()
    return bool(model_data)


def predict_attendance(class_image_np, tolerance=0.60, enrolled_student_ids=None):
    """
    Scans a classroom group photo or individual selfie, detects all faces,
    and matches them against registered student FaceID embeddings using
    nearest-neighbor 128-d Euclidean distance matching.

    If enrolled_student_ids is passed, candidates are strictly scoped to
    those enrolled students to avoid cross-class or duplicate identity errors.
    """
    encodings = get_face_embeddings(class_image_np)
    detected_student = {}

    model_data = get_trained_model()
    if not model_data or not encodings:
        return detected_student, [], len(encodings)

    X_train = model_data['X']
    y_train = model_data['y']

    # Filter candidates strictly to enrolled students if specified
    if enrolled_student_ids:
        enrolled_set = {int(s) for s in enrolled_student_ids}
        f_X, f_y = [], []
        for x_emb, sid in zip(X_train, y_train):
            if sid in enrolled_set:
                f_X.append(x_emb)
                f_y.append(sid)
        if f_X:
            X_train = f_X
            y_train = f_y

    all_students = sorted(list(set(y_train)))

    # Standard dlib 128-d Euclidean distance threshold (0.60 LFW benchmark)
    resemblance_threshold = tolerance

    for encoding in encodings:
        enc_arr = np.asarray(encoding, dtype=np.float64)
        if enc_arr.shape != (128,):
            continue

        dists = []
        for sid, k_emb in zip(y_train, X_train):
            k_arr = np.asarray(k_emb, dtype=np.float64)
            if k_arr.shape != (128,):
                continue
            d = float(np.linalg.norm(k_arr - enc_arr))
            dists.append((d, int(sid)))

        if dists:
            dists.sort()
            min_dist = dists[0][0]
            if min_dist <= resemblance_threshold:
                # Match closest student, plus any near-identical profile (e.g. duplicate account for same person)
                for d, sid in dists:
                    if d <= resemblance_threshold and d <= min_dist + 0.025:
                        curr_best = detected_student.get(sid, float('inf'))
                        if d < curr_best:
                            detected_student[sid] = round(d, 3)

    return detected_student, all_students, len(encodings)

