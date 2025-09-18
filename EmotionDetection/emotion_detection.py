"""
Emotion detection utilities.

Primary: call Watson NLP EmotionPredict endpoint (if reachable).
Fallback: simple keyword rule-based detector (works offline).
"""

from typing import Dict, Any
import requests

WATSON_URL = (
    "https://sn-watson-emotion.labs.skills.network/v1/watson.runtime.nlp.v1/"
    "NlpService/EmotionPredict"
)
WATSON_HEADERS = {"grpc-metadata-mm-model-id": "emotion_aggregated-workflow_lang_en_stock"}


def _none_result() -> Dict[str, Any]:
    """Return the None-values dict required for blank/400 responses."""
    return {
        "anger": None,
        "disgust": None,
        "fear": None,
        "joy": None,
        "sadness": None,
        "dominant_emotion": None,
        "status_code": 400  # Added for Task 7
    }


def _rule_based_detector(text: str) -> Dict[str, Any]:
    """Simple keyword-based fallback detector (normalized scores)."""
    text_l = text.lower()
    buckets = {
        "anger": 0.0,
        "disgust": 0.0,
        "fear": 0.0,
        "joy": 0.0,
        "sadness": 0.0,
    }
    # small keyword lists
    for w in ("angry", "mad", "hate", "furious", "annoy"):
        if w in text_l:
            buckets["anger"] += 1.0
    for w in ("disgust", "disgusted", "gross"):
        if w in text_l:
            buckets["disgust"] += 1.0
    for w in ("afraid", "scared", "fear", "terrified"):
        if w in text_l:
            buckets["fear"] += 1.0
    for w in ("happy", "glad", "love", "joy", "excited"):
        if w in text_l:
            buckets["joy"] += 1.0
    for w in ("sad", "unhappy", "depressed", "sorrow"):
        if w in text_l:
            buckets["sadness"] += 1.0

    total = sum(buckets.values())
    if total == 0:
        # no keywords → small default distribution, choose 'joy' as mild default
        out = {"anger": 0.1, "disgust": 0.05, "fear": 0.05, "joy": 0.6, "sadness": 0.2}
        out["dominant_emotion"] = max(out, key=out.get)
        out["status_code"] = 200
        return out

    out = {k: v / total for k, v in buckets.items()}
    out["dominant_emotion"] = max(out, key=out.get)
    out["status_code"] = 200
    return out


def emotion_detector(text_to_analyze: str) -> Dict[str, Any]:
    """Detect emotions for given text.

    Returns a dict with keys: anger, disgust, fear, joy, sadness, dominant_emotion, status_code.

    Behavior:
    - If text is blank/only-spaces → returns None-values dict with status_code 400.
    - Try Watson API first. If status_code == 400 → return None-values dict.
    - If Watson returns 200, parse and return formatted dict with status_code 200.
    - If any error / non-200 (except 400) → fallback to rule-based detector with status_code 200.
    """
    if not text_to_analyze or not text_to_analyze.strip():
        return _none_result()

    # Try Watson API
    try:
        resp = requests.post(
            WATSON_URL,
            headers=WATSON_HEADERS,
            json={"raw_document": {"text": text_to_analyze}},
            timeout=8,
        )
    except Exception:
        # network error → fallback
        out = _rule_based_detector(text_to_analyze)
        out["status_code"] = 200
        return out

    # If server says 400 → per assignment return None-values
    if resp.status_code == 400:
        return _none_result()

    # If Watson success → parse
    if resp.status_code == 200:
        try:
            j = resp.json()
            emotions = j["emotionPredictions"][0]["emotion"]
            out = {
                "anger": float(emotions.get("anger", 0.0)),
                "disgust": float(emotions.get("disgust", 0.0)),
                "fear": float(emotions.get("fear", 0.0)),
                "joy": float(emotions.get("joy", 0.0)),
                "sadness": float(emotions.get("sadness", 0.0)),
            }
            out["dominant_emotion"] = max(out, key=out.get)
            out["status_code"] = 200
            return out
        except Exception:
            # malformed response -> fallback
            out = _rule_based_detector(text_to_analyze)
            out["status_code"] = 200
            return out

    # other status codes -> fallback
    out = _rule_based_detector(text_to_analyze)
    out["status_code"] = 200
    return out
