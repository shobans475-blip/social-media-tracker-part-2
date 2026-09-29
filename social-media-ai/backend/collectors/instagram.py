import random
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from config.settings import settings

INSTAGRAM_CREATORS = [
    {"user_id": "usr_ananya_styles", "user_name": "Ananya Joshi", "handle": "@ananya_explores", "location": "Mumbai, Maharashtra", "age": 22, "gender": "female", "followers": 89000},
    {"user_id": "usr_divya_ecowarrior", "user_name": "Divya Nambiar", "handle": "@divya_green_roots", "location": "Kochi, Kerala", "age": 25, "gender": "female", "followers": 32000},
    {"user_id": "usr_chef_vikas", "user_name": "Chef Vikas Culinary", "handle": "@vikas_spices", "location": "New Delhi, Delhi", "age": 33, "gender": "male", "followers": 120000}
]

INSTAGRAM_SNIPPETS = [
    ("Weekend vibes in Old Kochi 🌊 Traditional architecture meeting sustainable street art. Support local artisans! #IncredibleIndia #SustainableTravel #Kerala", "en"),
    ("Spreading awareness on reducing single use plastics across local cafes! Drop a 💚 if you carry your own bottle. #ZeroWasteIndia #EcoFriendly", "en"),
    ("Exploring regional street food flavours in Chandni Chowk! The spice blends have 150 years of heritage. #DelhiFoodies #FoodLove", "en")
]

class InstagramCollector:
    def __init__(self):
        self.access_token = settings.instagram_access_token

    def generate_simulated_post(self, parent_post_id: Optional[str] = None) -> Dict[str, Any]:
        creator = random.choice(INSTAGRAM_CREATORS)
        caption, lang = random.choice(INSTAGRAM_SNIPPETS)
        post_num = random.randint(10000, 99999)

        return {
            "id": f"ig_{post_num}",
            "platform": "instagram",
            "platform_post_id": f"media_{post_num}",
            "user_id": creator["user_id"],
            "user_name": creator["user_name"],
            "handle": creator["handle"],
            "user_location": creator["location"],
            "user_age": creator["age"],
            "user_gender": creator["gender"],
            "user_followers": creator["followers"],
            "text": caption,
            "language": lang,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "likes": random.randint(500, 15000),
            "shares": random.randint(100, 2400),
            "comments": random.randint(50, 1800),
            "parent_post_id": parent_post_id
        }

    async def fetch_live(self) -> List[Dict[str, Any]]:
        return [self.generate_simulated_post()]

instagram_collector = InstagramCollector()
