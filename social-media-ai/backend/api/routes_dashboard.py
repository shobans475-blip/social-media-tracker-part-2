from typing import Optional, List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from database.database import get_db
from database.schemas import PostModel, UserModel
from services.sentiment_service import sentiment_service
from services.demographic_service import demographic_service
from services.trend_service import trend_service
from services.network_service import network_service
from collectors.twitter import twitter_collector
from collectors.telegram import telegram_collector
from collectors.instagram import instagram_collector
from collectors.youtube import youtube_collector

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])

@router.get("/summary")
def get_dashboard_summary(
    platform: Optional[str] = Query(None, description="Platform filter: all, twitter, telegram, instagram, youtube"),
    db: Session = Depends(get_db)
):
    """
    Returns overarching operational intelligence summary for dashboard telemetry
    """
    query = db.query(PostModel)
    if platform and platform.lower() != "all":
        query = query.filter(PostModel.platform == platform.lower())
    
    total_posts = query.count()
    
    # Platform volume distribution
    all_posts = db.query(PostModel).all()
    platform_breakdown = {}
    for p in all_posts:
        platform_breakdown[p.platform] = platform_breakdown.get(p.platform, 0) + 1

    # Sentiment overview
    sentiment_data = sentiment_service.get_sentiment_overview(db, platform)
    
    # Threat metrics
    threat_count = len(sentiment_data.get("threat_alerts", []))
    threat_status = "NORMAL"
    if threat_count >= 4:
        threat_status = "HIGH ALERT"
    elif threat_count >= 1:
        threat_status = "ELEVATED"

    # Trends overview
    trends_data = trend_service.get_trends(db, platform)
    
    # Network metrics overview
    net_data = network_service.get_network_graph(db, platform)

    return {
        "status": "success",
        "system_status": "ONLINE",
        "threat_level": threat_status,
        "kpis": {
            "total_posts_monitored": total_posts,
            "active_platforms": len(platform_breakdown),
            "threat_signals_detected": threat_count,
            "network_nodes_mapped": net_data["total_nodes"],
            "network_edges_active": net_data["total_edges"],
            "avg_sentiment_polarity": sentiment_data["avg_polarity"]
        },
        "platform_distribution": platform_breakdown,
        "sentiment": sentiment_data,
        "trends": trends_data,
        "network_preview": {
            "total_nodes": net_data["total_nodes"],
            "total_edges": net_data["total_edges"],
            "top_influencers": net_data["top_influencers"][:4]
        }
    }

@router.get("/feed")
def get_live_feed(
    limit: int = 15,
    platform: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Returns most recent posts with enriched sentiment and threat tags"""
    query = db.query(PostModel).order_by(PostModel.created_at.desc())
    if platform and platform.lower() != "all":
        query = query.filter(PostModel.platform == platform.lower())
    
    posts = query.limit(limit).all()
    items = []
    for p in posts:
        # Resolve user
        user = p.user
        sent = sentiment_service.analyze_single_text(p.text)
        s_data = sent["sentiment"]
        
        items.append({
            "id": p.id,
            "platform": p.platform,
            "platform_post_id": p.platform_post_id,
            "user_id": p.user_id,
            "user_name": user.username if user else "Verified Source",
            "handle": user.handle if user else f"@{p.user_id}",
            "user_location": user.inferred_location if user else "India",
            "user_followers": user.followers if user else 1200,
            "text": p.text,
            "language": p.language,
            "created_at": p.created_at.isoformat() if p.created_at else "",
            "likes": p.likes,
            "shares": p.shares,
            "comments": p.comments,
            "parent_post_id": p.parent_post_id,
            "sentiment_label": s_data["sentiment_label"],
            "compound_score": s_data["compound_score"],
            "toxicity_score": s_data["toxicity_score"],
            "hate_speech_flag": s_data["hate_speech_flag"],
            "misinformation_flag": s_data["misinformation_flag"]
        })
    
    return {"status": "success", "count": len(items), "posts": items}

@router.post("/inject-event")
def inject_demo_event(event_type: str = "random", db: Session = Depends(get_db)):
    """Allows demo judges/evaluators to inject simulated events on the fly"""
    generators = {
        "twitter": twitter_collector,
        "telegram": telegram_collector,
        "instagram": instagram_collector,
        "youtube": youtube_collector
    }
    
    if event_type in generators:
        item = generators[event_type].generate_simulated_post()
    else:
        collector = twitter_collector
        item = collector.generate_simulated_post()

    # Save to db
    user_id = item["user_id"]
    existing_user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not existing_user:
        u = UserModel(
            id=user_id,
            username=item["user_name"],
            handle=item["handle"],
            platform=item["platform"],
            followers=item["user_followers"],
            inferred_age=item["user_age"],
            inferred_gender=item["user_gender"],
            inferred_location=item["user_location"]
        )
        db.add(u)
        db.flush()

    new_post = PostModel(
        id=item["id"],
        platform=item["platform"],
        platform_post_id=item["platform_post_id"],
        user_id=user_id,
        text=item["text"],
        language=item["language"],
        likes=item["likes"],
        shares=item["shares"],
        comments=item["comments"],
        parent_post_id=item["parent_post_id"]
    )
    db.add(new_post)
    db.commit()
    
    return {"status": "success", "message": "Event injected into stream", "post": item}
