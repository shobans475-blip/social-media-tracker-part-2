from typing import Dict, Any, List
from sqlalchemy.orm import Session
from database.schemas import PostModel, UserModel
from models.network import network_model
from utils.helpers import extract_mentions

class NetworkService:
    def get_network_graph(self, db: Session, platform: str = None) -> Dict[str, Any]:
        """Builds directed NetworkX graph from database records and returns nodes/links"""
        post_query = db.query(PostModel)
        user_query = db.query(UserModel)

        if platform and platform.lower() != "all":
            post_query = post_query.filter(PostModel.platform == platform.lower())
            user_query = user_query.filter(UserModel.platform == platform.lower())

        posts = post_query.all()
        users = user_query.all()

        post_dicts = []
        for p in posts:
            post_dicts.append({
                "id": p.id,
                "user_id": p.user_id,
                "platform": p.platform,
                "parent_post_id": p.parent_post_id,
                "mentions": extract_mentions(p.text)
            })

        user_dicts = []
        for u in users:
            user_dicts.append({
                "id": u.id,
                "username": u.username,
                "handle": u.handle,
                "platform": u.platform,
                "followers": u.followers
            })

        network_model.build_graph(post_dicts, user_dicts)
        return network_model.export_visualization_data()

network_service = NetworkService()
