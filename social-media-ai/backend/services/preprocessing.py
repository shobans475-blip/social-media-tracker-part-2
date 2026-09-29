import re
from typing import Dict, Any, List
from utils.language import detect_language
from utils.helpers import clean_text, extract_hashtags, extract_mentions

# Basic Indian stopwords + English common stopwords
STOPWORDS = {
    "a", "an", "the", "and", "or", "but", "if", "because", "as", "what",
    "which", "this", "that", "these", "those", "then", "just", "so", "than",
    "such", "both", "through", "about", "for", "is", "of", "while", "during",
    "to", "from", "in", "out", "on", "off", "again", "further", "then", "once",
    "here", "there", "when", "where", "why", "how", "all", "any", "both", "each",
    "few", "more", "most", "other", "some", "such", "no", "nor", "not", "only",
    "own", "same", "so", "than", "too", "very", "s", "t", "can", "will", "just",
    "don", "should", "now", "are", "was", "were", "be", "been", "being", "have",
    "has", "had", "do", "does", "did", "doing", "with", "at", "by", "from",
    "ka", "ki", "ke", "ko", "se", "me", "mein", "par", "hai", "hain", "tha", "the", "thi"
}

class Preprocessor:
    def __init__(self):
        pass

    def process(self, text: str) -> Dict[str, Any]:
        """
        Cleans text, detects language, extracts hashtags, mentions,
        and generates filtered tokens.
        """
        cleaned = clean_text(text)
        lang_info = detect_language(text)
        hashtags = extract_hashtags(text)
        mentions = extract_mentions(text)

        # Tokenization (Unicode word tokens)
        raw_tokens = re.findall(r"[\w\u0900-\u0D7F]+", cleaned.lower())
        tokens = [t for t in raw_tokens if len(t) > 2 and t not in STOPWORDS]

        return {
            "raw_text": text,
            "cleaned_text": cleaned,
            "language": lang_info["code"],
            "language_name": lang_info["name"],
            "language_confidence": lang_info["confidence"],
            "hashtags": hashtags,
            "mentions": mentions,
            "tokens": tokens,
            "char_count": len(text),
            "word_count": len(raw_tokens)
        }

preprocessor = Preprocessor()
