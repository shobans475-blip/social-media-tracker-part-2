from typing import Dict, Any, List
from sqlalchemy.orm import Session
from database.schemas import PostModel, SentimentModel
from models.sentiment import sentiment_model
from services.preprocessing import preprocessor

class SentimentService:
    def analyze_single_text(self, text: str) -> Dict[str, Any]:
        """Runs preprocessing + sentiment + toxicity detection for arbitrary text"""
        prep = preprocessor.process(text)
        sent = sentiment_model.analyze(prep["cleaned_text"], prep["language"])
        return {
            "text": text,
            "preprocessed": prep,
            "sentiment": sent
        }

    def get_sentiment_overview(self, db: Session, platform: str = None) -> Dict[str, Any]:
        """Calculates global sentiment distribution, average polarity, and threat alerts"""
        query = db.query(PostModel)
        if platform and platform.lower() != "all":
            query = query.filter(PostModel.platform == platform.lower())
        posts = query.all()

        if not posts:
            return {
                "total_analyzed": 0,
                "distribution": {"positive": 0, "neutral": 0, "negative": 0},
                "percentages": {"positive": 0, "neutral": 0, "negative": 0},
                "avg_polarity": 0.0,
                "threat_alerts": []
            }

        counts = {"positive": 0, "neutral": 0, "negative": 0}
        total_polarity = 0.0
        threat_alerts = []

        for p in posts:
            res = sentiment_model.analyze(p.text, p.language)
            lbl = res["sentiment_label"]
            counts[lbl] = counts.get(lbl, 0) + 1
            total_polarity += res["compound_score"]

            if res["hate_speech_flag"] or res["misinformation_flag"] or res["toxicity_score"] > 0.6:
                threat_alerts.append({
                    "post_id": p.id,
                    "platform": p.platform,
                    "text": p.text[:120] + "..." if len(p.text) > 120 else p.text,
                    "toxicity": res["toxicity_score"],
                    "is_hate": res["hate_speech_flag"],
                    "is_misinfo": res["misinformation_flag"],
                    "created_at": p.created_at.isoformat() if p.created_at else ""
                })

        total = len(posts)
        return {
            "total_analyzed": total,
            "distribution": counts,
            "percentages": {k: round(v / total * 100, 1) for k, v in counts.items()},
            "avg_polarity": round(total_polarity / total, 2),
            "threat_alerts": threat_alerts[:8]
        }

sentiment_service = SentimentService()
