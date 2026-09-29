import random
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from config.settings import settings

TELEGRAM_CHANNELS = [
    {"user_id": "usr_tg_intel", "user_name": "Cyber Defense Watch", "handle": "t.me/cyberdefensein", "location": "New Delhi, Delhi", "age": 35, "gender": "organization", "followers": 92400},
    {"user_id": "usr_rahul_verma", "user_name": "Rahul Verma", "handle": "t.me/r_verma99", "location": "Pune, Maharashtra", "age": 29, "gender": "male", "followers": 1200},
    {"user_id": "usr_crypto_bot", "user_name": "MegaPump Signals", "handle": "t.me/pump_signals_fast", "location": "Unknown", "age": 19, "gender": "unknown", "followers": 18200}
]

TELEGRAM_SNIPPETS = [
    ("URGENT: New malware wave masquerading as income tax refund portal. Check official domain before entering banking OTPs! #CyberSecurity #Alert", "en"),
    ("🚨 500% RETURN TODAY ONLY! Send Bitcoin/USDT to verified wallet. Double bonus ending in 30 mins! Contact admin now! #CryptoScam", "en"),
    ("Disaster management authority issues red alert for coastal districts due to depression over Bay of Bengal. #DisasterManagement #IndiaAlert", "en"),
    ("टेलीग्राम ग्रुप्स में फ़ैल रही नकली भर्ती की सूचना। आधिकारिक वेबसाइट से ही पुष्टि करें। #FactCheck", "hi")
]

class TelegramCollector:
    def __init__(self):
        self.api_id = settings.telegram_api_id
        self.api_hash = settings.telegram_api_hash

    def generate_simulated_post(self, parent_post_id: Optional[str] = None) -> Dict[str, Any]:
        ch = random.choice(TELEGRAM_CHANNELS)
        text, lang = random.choice(TELEGRAM_SNIPPETS)
        post_num = random.randint(10000, 99999)

        return {
            "id": f"tg_{post_num}",
            "platform": "telegram",
            "platform_post_id": f"msg_{post_num}",
            "user_id": ch["user_id"],
            "user_name": ch["user_name"],
            "handle": ch["handle"],
            "user_location": ch["location"],
            "user_age": ch["age"],
            "user_gender": ch["gender"],
            "user_followers": ch["followers"],
            "text": text,
            "language": lang,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "likes": random.randint(15, 2300),
            "shares": random.randint(20, 3100),
            "comments": random.randint(5, 450),
            "parent_post_id": parent_post_id
        }

    async def fetch_live(self) -> List[Dict[str, Any]]:
        # In full production, Telethon or Pyrogram connects to MTProto
        return [self.generate_simulated_post()]

telegram_collector = TelegramCollector()
