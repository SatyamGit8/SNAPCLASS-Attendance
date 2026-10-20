import dlib
import numpy as np
import face_recognition_models
import streamlit as st
from src.database.db import get_all_students


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
    detector, sp, facerec = load_dlib_models()
    # Upsample by 1 to detect classroom faces; if none found, try upsample 2 for distant faces
    faces = detector(image_np, 1)
    if len(faces) == 0:
        faces = detector(image_np, 2)

    encodings = []
    for face in faces:
        shape = sp(image_np, face)
        face_descriptor = facerec.compute_face_descriptor(image_np, shape, 1)
        encodings.append(np.array(face_descriptor))
    return encodings


@st.cache_resource
def get_trained_model():
    X = []
    y = []

    student_db = get_all_students()
    if not student_db:
        return None

    for student in student_db:
        embedding = student.get('face_embedding')
        if embedding:
            X.append(np.array(embedding))
            y.append(student.get('student_id'))

    if len(X) == 0:
        return None

    return {'X': X, 'y': y}


def train_classifier():
    st.cache_resource.clear()
    model_data = get_trained_model()
    return bool(model_data)


def predict_attendance(class_image_np):
    """
    Scans a classroom group photo or individual selfie, detects all faces,
    and matches them against registered student FaceID embeddings using
    nearest-neighbor 128-d Euclidean distance matching.
    """
    encodings = get_face_embeddings(class_image_np)
    detected_student = {}

    model_data = get_trained_model()
    if not model_data or not encodings:
        return detected_student, [], len(encodings)

    X_train = model_data['X']
    y_train = model_data['y']
    all_students = sorted(list(set(y_train)))

    # Strict dlib 128-d Euclidean distance threshold to avoid false positives
    resemblance_threshold = 0.48

    for encoding in encodings:
        best_sid = None
        min_dist = float('inf')

        for sid, k_emb in zip(y_train, X_train):
            dist = float(np.linalg.norm(k_emb - encoding))
            if dist < min_dist:
                min_dist = dist
                best_sid = sid

        if min_dist <= resemblance_threshold and best_sid is not None:
            detected_student[int(best_sid)] = True

    return detected_student, all_students, len(encodings)
