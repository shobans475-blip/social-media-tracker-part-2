from typing import Dict, Any, List
from sqlalchemy.orm import Session
from database.schemas import UserModel, PostModel
from models.demographics import demographics_model

class DemographicService:
    def get_demographics(self, db: Session, platform: str = None) -> Dict[str, Any]:
        """Aggregates demographic statistics across all tracked users"""
        query = db.query(UserModel)
        if platform and platform.lower() != "all":
            query = query.filter(UserModel.platform == platform.lower())
        users = query.all()

        user_dicts = []
        for u in users:
            user_dicts.append({
                "id": u.id,
                "inferred_age": u.inferred_age,
                "inferred_gender": u.inferred_gender,
                "inferred_location": u.inferred_location,
                "bot_probability": u.bot_probability,
                "followers": u.followers
            })

        return demographics_model.aggregate_demographics(user_dicts)

demographic_service = DemographicService()
