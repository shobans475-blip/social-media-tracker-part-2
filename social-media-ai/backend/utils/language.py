import re
from typing import Dict, Any

# Unicode ranges for major Indian and global scripts
SCRIPT_RANGES = {
    "hi": (0x0900, 0x097F),  # Devanagari (Hindi, Marathi, Sanskrit)
    "bn": (0x0980, 0x09FF),  # Bengali, Assamese
    "pa": (0x0A00, 0x0A7F),  # Gurmukhi (Punjabi)
    "gu": (0x0A80, 0x0AFF),  # Gujarati
    "ta": (0x0B80, 0x0BFF),  # Tamil
    "te": (0x0C00, 0x0C7F),  # Telugu
    "kn": (0x0C80, 0x0CFF),  # Kannada
    "ml": (0x0D00, 0x0D7F),  # Malayalam
    "ar": (0x0600, 0x06FF),  # Arabic, Urdu
}

LANGUAGE_NAMES = {
    "en": "English",
    "hi": "Hindi",
    "hinglish": "Hinglish",
    "ta": "Tamil",
    "te": "Telugu",
    "bn": "Bengali",
    "gu": "Gujarati",
    "pa": "Punjabi",
    "kn": "Kannada",
    "ml": "Malayalam",
    "ar": "Urdu/Arabic",
    "unknown": "Unknown"
}

# Common Hinglish token heuristics
HINGLISH_KEYWORDS = {
    "kya", "hai", "nahi", "hota", "bhai", "yaar", "kaise", "karte", "yeh", "woh",
    "accha", "bahut", "sahi", "shukriya", "matlab", "kyun", "kuch", "apne", "wale"
}

def detect_language(text: str) -> Dict[str, Any]:
    """
    Detect the primary language of the social media text using script inspection
    and Hinglish heuristic classification.
    """
    if not text or not text.strip():
        return {"code": "en", "name": "English", "confidence": 1.0}

    counts = {lang: 0 for lang in SCRIPT_RANGES}
    latin_count = 0
    total_chars = 0

    for char in text:
        cp = ord(char)
        if char.isalnum():
            total_chars += 1
            if ("a" <= char <= "z") or ("A" <= char <= "Z"):
                latin_count += 1
            else:
                for lang, (start, end) in SCRIPT_RANGES.items():
                    if start <= cp <= end:
                        counts[lang] += 1
                        break

    if total_chars == 0:
        return {"code": "en", "name": "English", "confidence": 1.0}

    # Check non-Latin dominant script
    for lang, count in counts.items():
        if count / total_chars > 0.25:
            confidence = min(0.99, round(count / total_chars + 0.3, 2))
            return {
                "code": lang,
                "name": LANGUAGE_NAMES.get(lang, lang),
                "confidence": confidence
            }

    # Check for Hinglish
    tokens = [w.lower() for w in re.findall(r"\b[a-zA-Z]{3,}\b", text)]
    if tokens:
        hinglish_matches = sum(1 for t in tokens if t in HINGLISH_KEYWORDS)
        if hinglish_matches >= 2 or (len(tokens) <= 5 and hinglish_matches >= 1):
            return {
                "code": "hinglish",
                "name": "Hinglish (Hindi-English)",
                "confidence": 0.88
            }

    # Default to English
    return {
        "code": "en",
        "name": "English",
        "confidence": round(max(0.65, latin_count / max(1, total_chars)), 2)
    }
