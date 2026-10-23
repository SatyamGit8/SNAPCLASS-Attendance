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


def robust_preprocess_audio(audio_np, sr=16000):
    """
    Normalizes audio across different laptop microphones:
    1. Removes DC bias/drift
    2. Peak normalizes so quiet/loud laptop microphones produce consistent volume
    3. Trims long silences via webrtcvad with safe fallback if trimmed too aggressively
    """
    if audio_np is None or len(audio_np) == 0:
        return audio_np

    # 1. Remove DC bias
    audio_np = audio_np - np.mean(audio_np)

    # 2. Peak normalization to 0.95
    peak = float(np.max(np.abs(audio_np)))
    if peak > 0.001:
        audio_np = (audio_np / peak) * 0.95

    # 3. Resemblyzer preprocess_wav with fallback
    if preprocess_wav is not None:
        try:
            wav = preprocess_wav(audio_np)
            # If VAD mode 3 was too aggressive on a distant or quiet mic, keep normalized audio
            if len(wav) >= int(sr * 0.5):
                return wav
        except Exception:
            pass

    return audio_np


def get_voice_embedding(audio_bytes):
    try:
        encoder = load_voice_encoder()
        if encoder is None:
            st.warning("Voice encoder model is not available.")
            return None

        audio, sr = librosa.load(io.BytesIO(audio_bytes), sr=16000)
        wav = robust_preprocess_audio(audio, sr=16000)
        embedding = encoder.embed_utterance(wav)
        emb_norm = float(np.linalg.norm(embedding))
        if emb_norm > 0:
            embedding = embedding / emb_norm
        return embedding.tolist()
    except Exception as e:
        st.error(f'Voice recognition error: {e}')
        return None


def identify_speaker(new_embedding, candidates_dict, threshold=0.70, min_margin=0.025):
    """
    Matches speaker embedding against enrolled candidates using normalized cosine similarity.
    Calibrated to threshold 0.70 to reliably verify cross-device laptop microphones.
    Includes smart separation check to distinguish distinct speakers while allowing
    duplicate enrolled accounts of the same speaker.
    """
    if new_embedding is None or not candidates_dict:
        return None, 0.0

    new_emb = np.array(new_embedding, dtype=np.float32)
    norm_new = float(np.linalg.norm(new_emb))
    if norm_new == 0:
        return None, 0.0
    u_new = new_emb / norm_new

    best_sid = None
    best_score = -1.0
    second_sid = None
    second_best_score = -1.0
    parsed_candidates = {}

    for sid, stored_embedding in candidates_dict.items():
        if stored_embedding:
            s_emb = np.array(stored_embedding, dtype=np.float32)
            norm_s = float(np.linalg.norm(s_emb))
            if norm_s > 0:
                u_s = s_emb / norm_s
                parsed_candidates[sid] = u_s
                similarity = float(np.dot(u_new, u_s))
                if similarity > best_score:
                    second_best_score = best_score
                    second_sid = best_sid
                    best_score = similarity
                    best_sid = sid
                elif similarity > second_best_score:
                    second_best_score = similarity
                    second_sid = sid

    # Cross-device speaker check
    if best_score >= threshold and best_sid is not None:
        if second_best_score > 0 and (best_score - second_best_score) < min_margin:
            # If top two candidates themselves have high mutual similarity (>= 0.75),
            # they are duplicate accounts of the same person -> accept best_sid
            u_top1 = parsed_candidates.get(best_sid)
            u_top2 = parsed_candidates.get(second_sid)
            if u_top1 is not None and u_top2 is not None:
                mutual_sim = float(np.dot(u_top1, u_top2))
                if mutual_sim >= 0.75:
                    return best_sid, round(best_score, 3)
            return None, round(best_score, 3)

        return best_sid, round(best_score, 3)

    return None, round(best_score, 3)


def process_bulk_audio(audio_bytes, candidates_dict, threshold=0.70):
    """
    Analyzes classroom audio and recognizes enrolled student voices across laptops.
    """
    try:
        encoder = load_voice_encoder()
        if encoder is None:
            st.warning("Voice encoder model is not available. Please use Face Attendance.")
            return {}

        audio, sr = librosa.load(io.BytesIO(audio_bytes), sr=16000)

        # Discard completely silent audio clips
        if len(audio) == 0 or np.max(np.abs(audio)) < 0.005:
            return {}

        identified_results = {}

        # 1. First, check whole audio if between 0.8s and 12.0s
        total_duration = len(audio) / sr
        if total_duration >= 0.8:
            wav_full = robust_preprocess_audio(audio, sr=16000)
            if len(wav_full) >= sr * 0.5:
                emb_full = encoder.embed_utterance(wav_full)
                sid, score = identify_speaker(emb_full, candidates_dict, threshold=threshold)
                if sid:
                    identified_results[sid] = score

        # 2. Segment by voice activity for multiple speakers (min 0.8 second per utterance)
        segments = librosa.effects.split(audio, top_db=25)

        for start, end in segments:
            if (end - start) < sr * 0.8:
                continue

            segment_audio = audio[start:end]
            if np.max(np.abs(segment_audio)) < 0.01:
                continue

            wav = robust_preprocess_audio(segment_audio, sr=16000)
            if len(wav) < sr * 0.5:
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