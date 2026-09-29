from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from database.database import get_db
from services.trend_service import trend_service

router = APIRouter(prefix="/api/trends", tags=["Trends & Topic Modeling"])

@router.get("/")
def get_trends(
    platform: Optional[str] = Query(None, description="Filter by platform"),
    db: Session = Depends(get_db)
):
    """
    Returns extracted TF-IDF topics, ranked hashtags with velocity, and alert topics
    """
    data = trend_service.get_trends(db, platform)
    return {"status": "success", "data": data}
