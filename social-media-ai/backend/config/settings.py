import os
from pathlib import Path
from pydantic import BaseModel
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

class Settings(BaseModel):
    app_name: str = os.getenv("APP_NAME", "SIH Social Media AI Intelligence")
    environment: str = os.getenv("ENVIRONMENT", "development")
    host: str = os.getenv("HOST", "127.0.0.1")
    port: int = int(os.getenv("PORT", "8000"))
    
    # Storage
    database_url: str = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR.parent / 'data' / 'social_media.db'}")
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    use_in_memory_cache: bool = os.getenv("USE_IN_MEMORY_CACHE", "true").lower() in ("true", "1", "yes")
    
    # Stream settings
    stream_interval: float = float(os.getenv("STREAM_INTERVAL_SECONDS", "3.5"))
    enable_auto_simulation: bool = os.getenv("ENABLE_AUTO_SIMULATION", "true").lower() in ("true", "1", "yes")
    
    # AI Key (for Deep Multimodal & Threat Intelligence)
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")

    # External API Keys (Hybrid fallback)
    twitter_bearer_token: str = os.getenv("TWITTER_BEARER_TOKEN", "")
    telegram_api_id: str = os.getenv("TELEGRAM_API_ID", "")
    telegram_api_hash: str = os.getenv("TELEGRAM_API_HASH", "")
    instagram_access_token: str = os.getenv("INSTAGRAM_ACCESS_TOKEN", "")
    youtube_api_key: str = os.getenv("YOUTUBE_API_KEY", "")

settings = Settings()
