from typing import Optional
from pydantic import BaseModel
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from database.database import get_db
from services.sentiment_service import sentiment_service
from config.settings import settings

router = APIRouter(prefix="/api/sentiment", tags=["Sentiment Analysis"])

class TextAnalyzeRequest(BaseModel):
    text: str
    deep_ai: Optional[bool] = False

@router.get("/metrics")
def get_sentiment_metrics(
    platform: Optional[str] = Query(None, description="Filter by platform"),
    db: Session = Depends(get_db)
):
    """Returns distribution, polarity, and threat alerts"""
    return sentiment_service.get_sentiment_overview(db, platform)

@router.post("/analyze")
async def analyze_custom_text(payload: TextAnalyzeRequest):
    """
    On-demand NLP analyzer for judge evaluations:
    Extracts entities, sentiment, toxicity, language, and AI threat assessment.
    """
    base_result = sentiment_service.analyze_single_text(payload.text)
    
    # If Gemini API key is configured and requested or available
    gemini_summary = None
    if settings.gemini_api_key and len(payload.text.strip()) > 5:
        try:
            # We can optionally call Google Gemini if key is active
            import google.genai as genai
            client = genai.Client(api_key=settings.gemini_api_key)
            prompt = (
                f"Analyze this social media text in 2-3 concise bullet points for intent, underlying sentiment, and risk/threat level:\n\n"
                f"\"{payload.text}\""
            )
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            if response and response.text:
                gemini_summary = response.text.strip()
        except Exception:
            gemini_summary = None

    return {
        "status": "success",
        "analysis": base_result,
        "gemini_deep_intel": gemini_summary
    }
