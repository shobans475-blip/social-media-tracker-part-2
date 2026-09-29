from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from database.database import get_db
from services.demographic_service import demographic_service

router = APIRouter(prefix="/api/demographics", tags=["Demographics & AI Profiling"])

@router.get("/")
def get_demographics(
    platform: Optional[str] = Query(None, description="Filter by platform"),
    db: Session = Depends(get_db)
):
    """
    Returns age cohort distribution, gender estimates, regional geo clusters, and bot detection
    """
    data = demographic_service.get_demographics(db, platform)
    return {"status": "success", "demographics": data}
