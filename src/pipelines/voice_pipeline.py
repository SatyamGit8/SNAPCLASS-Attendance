import sys
import os
import types

# Ensure pkg_resources is available for webrtcvad and other legacy libraries
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

try:
    from resemblyzer import VoiceEncoder, preprocess_wav
    VOICE_AVAILABLE = True
except Exception:
    VOICE_AVAILABLE = False
    VoiceEncoder = None
    preprocess_wav = None

import numpy as np 
import io
try:
    import librosa
except ImportError:
    librosa = None
import streamlit as st


@st.cache_resource
def load_voice_encoder():
    if not VOICE_AVAILABLE or VoiceEncoder is None:
        return None
    return VoiceEncoder()


def get_voice_embedding(audio_bytes):
    try:
        encoder = load_voice_encoder()
        if encoder is None or preprocess_wav is None:
            st.warning("Voice encoder model is not available.")
            return None

        audio, sr = librosa.load(io.BytesIO(audio_bytes), sr=16000)
        wav = preprocess_wav(audio)
        embedding = encoder.embed_utterance(wav)
        emb_norm = np.linalg.norm(embedding)
        if emb_norm > 0:
            embedding = embedding / emb_norm
        return embedding.tolist()
    except Exception as e:
        st.error(f'Voice recognition error: {e}')
        return None


def identify_speaker(new_embedding, candidates_dict, threshold=0.76, min_margin=0.04):
    """
    Matches speaker embedding against enrolled candidates using normalized cosine similarity.
    Requires similarity >= threshold (0.76) AND a separation margin from runner-up
    to avoid false identification.
    """
    if new_embedding is None or not candidates_dict:
        return None, 0.0

    new_emb = np.array(new_embedding, dtype=np.float32)
    norm_new = np.linalg.norm(new_emb)
    if norm_new == 0:
        return None, 0.0
    u_new = new_emb / norm_new

    best_sid = None
    best_score = -1.0
    second_best_score = -1.0

    for sid, stored_embedding in candidates_dict.items():
        if stored_embedding:
            s_emb = np.array(stored_embedding, dtype=np.float32)
            norm_s = np.linalg.norm(s_emb)
            if norm_s > 0:
                similarity = float(np.dot(u_new, s_emb / norm_s))
                if similarity > best_score:
                    second_best_score = best_score
                    best_score = similarity
                    best_sid = sid
                elif similarity > second_best_score:
                    second_best_score = similarity

    # High precision check: must exceed threshold (0.76) AND be clearly separated from second place
    if best_score >= threshold:
        if second_best_score < 0 or (best_score - second_best_score) >= min_margin:
            return best_sid, round(best_score, 3)

    return None, round(best_score, 3)


def process_bulk_audio(audio_bytes, candidates_dict, threshold=0.76):
    """
    Analyzes classroom audio and recognizes enrolled student voices.
    High precision 0.76 threshold prevents false identity matches.
    """
    try:
        encoder = load_voice_encoder()
        if encoder is None or preprocess_wav is None:
            st.warning("Voice encoder model is not available. Please use Face Attendance.")
            return {}

        audio, sr = librosa.load(io.BytesIO(audio_bytes), sr=16000)

        # Discard silent audio clips
        if len(audio) == 0 or np.max(np.abs(audio)) < 0.01:
            return {}

        identified_results = {}

        # 1. First, check whole audio if between 1.0s and 10.0s
        total_duration = len(audio) / sr
        if total_duration >= 1.0:
            wav_full = preprocess_wav(audio)
            if len(wav_full) >= sr * 0.8:
                emb_full = encoder.embed_utterance(wav_full)
                sid, score = identify_speaker(emb_full, candidates_dict, threshold=threshold)
                if sid:
                    identified_results[sid] = score

        # 2. Segment by voice activity for multiple speakers (min 1.0 second per utterance)
        segments = librosa.effects.split(audio, top_db=25)

        for start, end in segments:
            if (end - start) < sr * 1.0:
                continue

            segment_audio = audio[start:end]
            if np.max(np.abs(segment_audio)) < 0.02:
                continue

            wav = preprocess_wav(segment_audio)
            if len(wav) < sr * 0.8:
                continue

            embedding = encoder.embed_utterance(wav)
            sid, score = identify_speaker(embedding, candidates_dict, threshold=threshold)

            if sid:
                if sid not in identified_results or score > identified_results[sid]:
                    identified_results[sid] = score

        return identified_results
    except Exception as e:
        st.error(f'Voice analysis error: {e}')
        return {}