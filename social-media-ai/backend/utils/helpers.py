import re
from datetime import datetime, timezone
from typing import List, Dict, Any

def clean_text(text: str) -> str:
    """Removes messy escape characters, extra whitespace, while retaining hashtags & mentions"""
    if not text:
        return ""
    text = re.sub(r"https?://\S+|www\.\S+", "", text) # strip raw URLs for NLP
    text = re.sub(r"\s+", " ", text)
    return text.strip()

def extract_hashtags(text: str) -> List[str]:
    """Extracts all hashtags in lowercase without '#', retaining valid alphanumeric unicode"""
    if not text:
        return []
    matches = re.findall(r"#([\w\u0900-\u0D7F]+)", text)
    return [m.lower() for m in matches]

def extract_mentions(text: str) -> List[str]:
    """Extracts all @mentions"""
    if not text:
        return []
    matches = re.findall(r"@([a-zA-Z0-9_]+)", text)
    return [m.lower() for m in matches]

def format_number(val: int) -> str:
    """Formats large metric numbers into readable strings: e.g. 1.2K, 3.4M"""
    if val >= 1_000_000:
        return f"{val / 1_000_000:.1f}M"
    if val >= 1_000:
        return f"{val / 1_000:.1f}K"
    return str(val)

def iso_now() -> str:
    return datetime.now(timezone.utc).isoformat()
