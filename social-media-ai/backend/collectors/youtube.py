import random
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from config.settings import settings

YOUTUBE_CHANNELS = [
    {"user_id": "usr_desh_samachar", "user_name": "Tech Bharat Review", "handle": "@TechBharatOfficial", "location": "Noida, Uttar Pradesh", "age": 34, "gender": "male", "followers": 250000},
    {"user_id": "usr_science_daily", "user_name": "ISRO Space Enthusiasts", "handle": "@SpaceBharat360", "location": "Bengaluru, Karnataka", "age": 27, "gender": "organization", "followers": 310000}
]

YOUTUBE_SNIPPETS = [
    ("India's reusable launch vehicle test flight declared an unprecedented success! Real-time flight trajectory telemetry analyzed. #ISRO #SpaceTech #IndiaInSpace", "en"),
    ("Next-gen UPI Soundbox 2.0 with instant vernacular multi-lingual voice alerts demonstrated at the Global Fintech Fest! #Fintech #DigitalIndia", "en"),
    ("Cyber hygiene tutorial: 5 mandatory steps to safeguard your WhatsApp and mobile banking apps from SIM swap scams. #CyberSecurityAwareness", "en")
]

class YouTubeCollector:
    def __init__(self):
        self.api_key = settings.youtube_api_key

    def generate_simulated_post(self, parent_post_id: Optional[str] = None) -> Dict[str, Any]:
        ch = random.choice(YOUTUBE_CHANNELS)
        title, lang = random.choice(YOUTUBE_SNIPPETS)
        post_num = random.randint(10000, 99999)

        return {
            "id": f"yt_{post_num}",
            "platform": "youtube",
            "platform_post_id": f"vid_{post_num}",
            "user_id": ch["user_id"],
            "user_name": ch["user_name"],
            "handle": ch["handle"],
            "user_location": ch["location"],
            "user_age": ch["age"],
            "user_gender": ch["gender"],
            "user_followers": ch["followers"],
            "text": title,
            "language": lang,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "likes": random.randint(300, 18000),
            "shares": random.randint(50, 4200),
            "comments": random.randint(20, 2100),
            "parent_post_id": parent_post_id
        }

    async def fetch_live(self) -> List[Dict[str, Any]]:
        return [self.generate_simulated_post()]

youtube_collector = YouTubeCollector()
