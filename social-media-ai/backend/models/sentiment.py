import re
from typing import Dict, Any

POSITIVE_WORDS = {
    "great", "awesome", "excellent", "breakthrough", "congratulations", "proud", "amazing",
    "growth", "victory", "success", "innovative", "love", "good", "best", "momentum",
    "indigenous", "slashing", "game changer", "thriving", "kudos", "grateful", "beautiful",
    "बधाई", "शानदार", "सफल", "विकास", "गौरव", "उत्कृष्ट", "बेहतरीन", "प्यार", "सुखद", "बढ़िया"
}

NEGATIVE_WORDS = {
    "terrible", "awful", "horrible", "smog", "pollution", "severe", "sluggish", "disappointing",
    "crisis", "failure", "danger", "fraud", "phishing", "scam", "breathing difficulty",
    "water logging", "damage", "attack", "threat", "hate", "fake", "illegal", "corrupt",
    "धोखा", "घोटाला", "अफवाह", "गंभीर", "कठिन", "बुरा", "प्रदूषण", "हानिकारक", "अपराध", "विनाश"
}

TOXIC_PATTERNS = [
    r"\b(idiot|stupid|scam|fraud|phishing|cheat|bastard|kill|threat|ruin)\b",
    r"\b(fake|lies|propaganda|loot|chutiya|bakwas)\b"
]

MISINFO_PATTERNS = [
    r"\b(guaranteed profit|invest.*get.*24 hours|easy money|urgent forward|shutting down water|free recharge)\b",
    r"\b(बिना पुष्टि किए|अफवाह|फर्जी संदेश)\b"
]

class SentimentAnalyzer:
    def analyze(self, text: str, language: str = "en") -> Dict[str, Any]:
        """
        Analyzes social media text for sentiment, polarity compound score,
        toxicity rating, hate speech, and misinformation cues.
        """
        lower = text.lower()
        words = re.findall(r"[\w\u0900-\u0D7F]+", lower)

        pos_count = sum(1 for w in words if w in POSITIVE_WORDS)
        neg_count = sum(1 for w in words if w in NEGATIVE_WORDS)

        # Multi-word phrase boosts
        if "game changer" in lower or "big boost" in lower:
            pos_count += 2
        if "breathing difficulty" in lower or "water logging" in lower or "deepfake loan fraud" in lower:
            neg_count += 2

        total_emotional = pos_count + neg_count
        if total_emotional == 0:
            compound = 0.0
            sentiment_label = "neutral"
            pos_score, neu_score, neg_score = 0.1, 0.8, 0.1
        else:
            diff = pos_count - neg_count
            compound = round(diff / (total_emotional + 1.0), 3)
            if compound >= 0.15:
                sentiment_label = "positive"
            elif compound <= -0.15:
                sentiment_label = "negative"
            else:
                sentiment_label = "neutral"

            pos_score = round(max(0.05, pos_count / (total_emotional + 0.5)), 2)
            neg_score = round(max(0.05, neg_count / (total_emotional + 0.5)), 2)
            neu_score = round(max(0.1, 1.0 - (pos_score + neg_score)), 2)

        # Toxicity & hate speech scoring
        toxic_matches = 0
        for pat in TOXIC_PATTERNS:
            if re.search(pat, lower):
                toxic_matches += 1
        toxicity_score = round(min(1.0, toxic_matches * 0.35 + (0.3 if neg_count > 2 else 0.0)), 2)
        hate_speech_flag = toxicity_score >= 0.70

        # Misinformation indicator
        misinfo_flag = False
        for pat in MISINFO_PATTERNS:
            if re.search(pat, lower):
                misinfo_flag = True
                break

        return {
            "sentiment_label": sentiment_label,
            "compound_score": compound,
            "positive_score": pos_score,
            "neutral_score": neu_score,
            "negative_score": neg_score,
            "toxicity_score": toxicity_score,
            "hate_speech_flag": hate_speech_flag,
            "misinformation_flag": misinfo_flag
        }

sentiment_model = SentimentAnalyzer()
