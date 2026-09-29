from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from database.database import get_db
from services.network_service import network_service

router = APIRouter(prefix="/api/network", tags=["Network & Link Analysis"])

@router.get("/graph")
def get_network_graph(
    platform: Optional[str] = Query(None, description="Filter by platform"),
    db: Session = Depends(get_db)
):
    """
    Returns NetworkX graph data (nodes, links, clusters, PageRank, influencers)
    """
    data = network_service.get_network_graph(db, platform)
    return {"status": "success", "graph": data}
