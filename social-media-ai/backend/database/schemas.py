from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from sqlalchemy import (
    Column, String, Integer, Float, DateTime, Text, Boolean, ForeignKey
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

# ==========================================
# SQLAlchemy ORM Models
# ==========================================

class PostModel(Base):
    """
    Exact schema specified by user:
    posts
    --------------------------------
    id, platform, platform_post_id, user_id, text, language,
    created_at, likes, shares, comments, parent_post_id
    """
    __tablename__ = "posts"

    id = Column(String(64), primary_key=True, index=True)
    platform = Column(String(32), index=True, nullable=False) # twitter, telegram, instagram, youtube
    platform_post_id = Column(String(64), index=True, nullable=True)
    user_id = Column(String(64), ForeignKey("users.id", ondelete="SET NULL"), index=True, nullable=True)
    text = Column(Text, nullable=False)
    language = Column(String(16), default="en", index=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    likes = Column(Integer, default=0)
    shares = Column(Integer, default=0)
    comments = Column(Integer, default=0)
    parent_post_id = Column(String(64), nullable=True, index=True)

    # Relationships
    user = relationship("UserModel", back_populates="posts")
    sentiment = relationship("SentimentModel", back_populates="post", uselist=False, cascade="all, delete-orphan")


class UserModel(Base):
    __tablename__ = "users"

    id = Column(String(64), primary_key=True, index=True)
    username = Column(String(128), nullable=False)
    handle = Column(String(128), index=True)
    platform = Column(String(32), index=True)
    followers = Column(Integer, default=0)
    following = Column(Integer, default=0)
    inferred_age = Column(Integer, default=25)
    inferred_gender = Column(String(16), default="unknown")
    inferred_location = Column(String(128), default="India")
    bot_probability = Column(Float, default=0.05)
    verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    posts = relationship("PostModel", back_populates="user")


class SentimentModel(Base):
    __tablename__ = "sentiments"

    id = Column(String(64), primary_key=True)
    post_id = Column(String(64), ForeignKey("posts.id", ondelete="CASCADE"), unique=True, index=True)
    sentiment_label = Column(String(32), index=True) # positive, negative, neutral
    compound_score = Column(Float, default=0.0)
    positive_score = Column(Float, default=0.0)
    negative_score = Column(Float, default=0.0)
    neutral_score = Column(Float, default=0.0)
    toxicity_score = Column(Float, default=0.0)
    hate_speech_flag = Column(Boolean, default=False)
    misinformation_flag = Column(Boolean, default=False)

    post = relationship("PostModel", back_populates="sentiment")


class TrendModel(Base):
    __tablename__ = "trends"

    id = Column(String(64), primary_key=True)
    topic = Column(String(128), index=True, unique=True)
    hashtag = Column(String(128), index=True)
    volume = Column(Integer, default=1)
    velocity = Column(Float, default=1.0) # growth per hour
    sentiment_score = Column(Float, default=0.0)
    dominant_platform = Column(String(32), default="all")
    first_seen = Column(DateTime, default=datetime.utcnow)
    last_seen = Column(DateTime, default=datetime.utcnow)


class NetworkEdgeModel(Base):
    __tablename__ = "network_edges"

    id = Column(String(64), primary_key=True)
    source_id = Column(String(64), index=True)
    target_id = Column(String(64), index=True)
    relation_type = Column(String(32)) # reply, retweet, forward, mention, quote
    weight = Column(Float, default=1.0)
    created_at = Column(DateTime, default=datetime.utcnow)


# ==========================================
# Pydantic Schemas for Validation & APIs
# ==========================================

class PostCreate(BaseModel):
    id: Optional[str] = None
    platform: str
    platform_post_id: Optional[str] = None
    user_id: Optional[str] = None
    text: str
    language: Optional[str] = "en"
    created_at: Optional[datetime] = None
    likes: Optional[int] = 0
    shares: Optional[int] = 0
    comments: Optional[int] = 0
    parent_post_id: Optional[str] = None

class PostResponse(BaseModel):
    id: str
    platform: str
    platform_post_id: Optional[str] = None
    user_id: Optional[str] = None
    text: str
    language: str
    created_at: datetime
    likes: int
    shares: int
    comments: int
    parent_post_id: Optional[str] = None

    class Config:
        from_attributes = True

class LivePostItem(BaseModel):
    id: str
    platform: str
    platform_post_id: Optional[str] = None
    user_id: Optional[str] = None
    user_name: Optional[str] = "Anonymous"
    handle: Optional[str] = "@user"
    user_location: Optional[str] = "India"
    text: str
    language: str
    created_at: str
    likes: int
    shares: int
    comments: int
    parent_post_id: Optional[str] = None
    sentiment: Optional[str] = "neutral"
    sentiment_score: Optional[float] = 0.0
    toxicity: Optional[float] = 0.0
    threat_flag: Optional[bool] = False
