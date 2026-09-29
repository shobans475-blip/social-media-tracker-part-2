import random
import time
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
import httpx
from config.settings import settings

TWITTER_AUTHORS = [
    {"user_id": "usr_tech_guru", "user_name": "Aarav Sharma", "handle": "@aarav_tech", "location": "Bengaluru, Karnataka", "age": 28, "gender": "male", "followers": 45200},
    {"user_id": "usr_priya_m", "user_name": "Priya Mukherjee", "handle": "@priya_m_ai", "location": "Kolkata, West Bengal", "age": 24, "gender": "female", "followers": 8700},
    {"user_id": "usr_rohit_delhi", "user_name": "Rohit Malhotra", "handle": "@rohit_delhi_nc", "location": "Delhi NCR", "age": 31, "gender": "male", "followers": 15400},
    {"user_id": "usr_kavita_r", "user_name": "Kavita Reddy", "handle": "@kavita_hyderabad", "location": "Hyderabad, Telangana", "age": 26, "gender": "female", "followers": 6300},
    {"user_id": "usr_vikram_singh", "user_name": "Vikram Rathore", "handle": "@vikram_defence", "location": "Jaipur, Rajasthan", "age": 40, "gender": "male", "followers": 61200}
]

TWITTER_SNIPPETS = [
    ("Breakthrough in semiconductor packaging plant in Gujarat! Over 15,000 high-tech jobs expected. #SemiconIndia #TechNews", "en"),
    ("Delhi smog reaching hazardous limits. Citizens demand immediate artificial rain and construction audits. #DelhiAirPollution #CleanAir", "en"),
    ("Indian digital health stack registers 100M active records. Seamless tele-consultation across rural PHCs! #DigitalIndia", "en"),
    ("भारी बारिश के कारण कई क्षेत्रों में जलभराव की समस्या। कृपया सतर्क रहें और हेल्पलाइन 1070 पर संपर्क करें। #FloodAlert #WeatherUpdate", "hi"),
    ("New open weights Indian language model released today. Supports 22 scheduled languages with benchmark topping accuracy! @aarav_tech #AIIndia", "en")
]

class TwitterCollector:
    def __init__(self):
        self.bearer_token = settings.twitter_bearer_token

    def generate_simulated_post(self, parent_post_id: Optional[str] = None) -> Dict[str, Any]:
        """Generates realistic synthetic X/Twitter data for continuous streaming demo"""
        author = random.choice(TWITTER_AUTHORS)
        snippet, lang = random.choice(TWITTER_SNIPPETS)
        post_num = random.randint(10000, 99999)

        return {
            "id": f"tw_{post_num}",
            "platform": "twitter",
            "platform_post_id": f"1790{post_num}",
            "user_id": author["user_id"],
            "user_name": author["user_name"],
            "handle": author["handle"],
            "user_location": author["location"],
            "user_age": author["age"],
            "user_gender": author["gender"],
            "user_followers": author["followers"],
            "text": snippet,
            "language": lang,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "likes": random.randint(50, 4500),
            "shares": random.randint(10, 1200),
            "comments": random.randint(5, 340),
            "parent_post_id": parent_post_id
        }

    async def fetch_live(self, query: str = "India tech") -> List[Dict[str, Any]]:
        """Pluggable live Twitter API v2 fetcher when bearer token is present"""
        if not self.bearer_token:
            return [self.generate_simulated_post()]
        
        try:
            url = f"https://api.twitter.com/2/tweets/search/recent?query={query}&tweet.fields=created_at,public_metrics,lang"
            headers = {"Authorization": f"Bearer {self.bearer_token}"}
            async with httpx.AsyncClient() as client:
                res = await client.get(url, headers=headers, timeout=10)
                if res.status_code == 200:
                    data = res.json().get("data", [])
                    return [
                        {
                            "id": f"tw_{item['id']}",
                            "platform": "twitter",
                            "platform_post_id": item["id"],
                            "user_id": f"usr_{item.get('author_id', 'unknown')}",
                            "text": item.get("text", ""),
                            "language": item.get("lang", "en"),
                            "created_at": item.get("created_at"),
                            "likes": item.get("public_metrics", {}).get("like_count", 0),
                            "shares": item.get("public_metrics", {}).get("retweet_count", 0),
                            "comments": item.get("public_metrics", {}).get("reply_count", 0),
                            "parent_post_id": None
                        }
                        for item in data
                    ]
        except Exception:
            pass
        return [self.generate_simulated_post()]

twitter_collector = TwitterCollector()
