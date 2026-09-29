from typing import Dict, Any, List
from sqlalchemy.orm import Session
from database.schemas import PostModel
from models.trends import trend_model
from utils.helpers import extract_hashtags

class TrendService:
    def get_trends(self, db: Session, platform: str = None) -> Dict[str, Any]:
        """Extracts top topics and ranked hashtags from posts"""
        query = db.query(PostModel)
        if platform and platform.lower() != "all":
            query = query.filter(PostModel.platform == platform.lower())
        posts = query.all()

        texts = [p.text for p in posts]
        all_hashtags = []
        for p in posts:
            all_hashtags.extend(extract_hashtags(p.text))

        top_topics = trend_model.extract_top_topics(texts, top_n=6)
        ranked_hashtags = trend_model.rank_hashtags(all_hashtags, top_n=8)

        # Detect emerging critical alert trends
        critical_alerts = [
            h for h in ranked_hashtags if h["is_alert"]
        ]

        return {
            "top_topics": top_topics,
            "ranked_hashtags": ranked_hashtags,
            "critical_alerts": critical_alerts,
            "total_posts_analyzed": len(posts)
        }

trend_service = TrendService()
