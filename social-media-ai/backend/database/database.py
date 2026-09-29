import json
import logging
from pathlib import Path
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from config.settings import settings
from database.schemas import (
    Base, PostModel, UserModel, SentimentModel, TrendModel, NetworkEdgeModel
)

logger = logging.getLogger("database")

# Ensure data directory exists
db_url = settings.database_url
connect_args = {}
if db_url.startswith("sqlite"):
    connect_args["check_same_thread"] = False
    # Ensure folder exists
    db_file_path = db_url.replace("sqlite:///", "")
    Path(db_file_path).parent.mkdir(parents=True, exist_ok=True)

try:
    engine = create_engine(db_url, connect_args=connect_args)
except Exception as e:
    logger.warning(f"Could not connect to {db_url}, falling back to local SQLite: {e}")
    fallback_db = Path(__file__).resolve().parent.parent.parent / "data" / "social_media.db"
    fallback_db.parent.mkdir(parents=True, exist_ok=True)
    engine = create_engine(f"sqlite:///{fallback_db}", connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Create all tables and seed sample data if database is empty"""
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        existing_count = db.query(PostModel).count()
        if existing_count == 0:
            seed_data_file = Path(__file__).resolve().parent.parent.parent / "data" / "sample_social_data.json"
            if seed_data_file.exists():
                with open(seed_data_file, "r", encoding="utf-8") as f:
                    posts_data = json.load(f)
                
                for item in posts_data:
                    # Create or get user
                    user_id = item.get("user_id") or f"usr_{item['id']}"
                    existing_user = db.query(UserModel).filter(UserModel.id == user_id).first()
                    if not existing_user:
                        new_user = UserModel(
                            id=user_id,
                            username=item.get("user_name", "Anonymous"),
                            handle=item.get("handle", f"@{user_id}"),
                            platform=item["platform"],
                            followers=item.get("user_followers", 1000),
                            inferred_age=item.get("user_age", 25),
                            inferred_gender=item.get("user_gender", "unknown"),
                            inferred_location=item.get("user_location", "India"),
                            bot_probability=0.04
                        )
                        db.add(new_user)
                        db.flush()

                    created_dt = datetime.fromisoformat(item["created_at"].replace("Z", "+00:00")) if "created_at" in item else datetime.utcnow()
                    
                    # Create Post
                    post = PostModel(
                        id=item["id"],
                        platform=item["platform"],
                        platform_post_id=item.get("platform_post_id"),
                        user_id=user_id,
                        text=item["text"],
                        language=item.get("language", "en"),
                        created_at=created_dt,
                        likes=item.get("likes", 0),
                        shares=item.get("shares", 0),
                        comments=item.get("comments", 0),
                        parent_post_id=item.get("parent_post_id")
                    )
                    db.add(post)

                    # Build edge if replying or forwarding
                    if item.get("parent_post_id"):
                        edge = NetworkEdgeModel(
                            id=f"edge_{item['id']}_{item['parent_post_id']}",
                            source_id=user_id,
                            target_id=item["parent_post_id"],
                            relation_type="reply_or_repost",
                            weight=1.5
                        )
                        db.add(edge)

                db.commit()
                logger.info(f"Database initialized and seeded with {len(posts_data)} initial records.")
    except Exception as err:
        db.rollback()
        logger.error(f"Error during database initialization/seeding: {err}")
    finally:
        db.close()
