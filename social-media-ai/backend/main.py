import asyncio
import json
import logging
from pathlib import Path
from contextlib import asynccontextmanager
from typing import List

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse

from config.settings import settings
from database.database import init_db, SessionLocal
from database.schemas import PostModel, UserModel
from api.routes_dashboard import router as dashboard_router
from api.routes_sentiment import router as sentiment_router
from api.routes_trends import router as trends_router
from api.routes_demographics import router as demographics_router
from api.routes_network import router as network_router
from collectors.twitter import twitter_collector
from collectors.telegram import telegram_collector
from collectors.instagram import instagram_collector
from collectors.youtube import youtube_collector
from services.sentiment_service import sentiment_service

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("main")

BASE_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = BASE_DIR.parent / "frontend"

# Active WebSocket connections
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        dead_connections = []
        for connection in self.active_connections:
            try:
                await connection.send_text(json.dumps(message))
            except Exception:
                dead_connections.append(connection)
        for dead in dead_connections:
            self.disconnect(dead)

manager = ConnectionManager()

# Background stream simulator
async def background_stream_worker():
    """Generates continuous social media stream events and pushes to database + WebSockets"""
    collectors = [twitter_collector, telegram_collector, instagram_collector, youtube_collector]
    while True:
        try:
            await asyncio.sleep(settings.stream_interval)
            import random
            collector = random.choice(collectors)
            item = collector.generate_simulated_post()
            
            # Enrich with sentiment
            sent = sentiment_service.analyze_single_text(item["text"])
            s_data = sent["sentiment"]
            item["sentiment"] = s_data["sentiment_label"]
            item["sentiment_score"] = s_data["compound_score"]
            item["toxicity"] = s_data["toxicity_score"]
            item["threat_flag"] = s_data["hate_speech_flag"] or s_data["misinformation_flag"] or s_data["toxicity_score"] > 0.65

            # Save to database
            db = SessionLocal()
            try:
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
            except Exception as e:
                db.rollback()
                logger.error(f"Error persisting simulated post: {e}")
            finally:
                db.close()

            # Broadcast to UI
            await manager.broadcast({
                "type": "NEW_POST",
                "post": item
            })
        except asyncio.CancelledError:
            break
        except Exception as ex:
            logger.error(f"Error in stream worker: {ex}")
            await asyncio.sleep(4)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing database tables and seeding sample data...")
    init_db()
    task = None
    if settings.enable_auto_simulation:
        logger.info(f"Starting social media live stream simulation worker (every {settings.stream_interval}s)...")
        task = asyncio.create_task(background_stream_worker())
    yield
    if task:
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass

app = FastAPI(
    title=settings.app_name,
    description="Smart India Hackathon - Social Media Intelligence, NLP, Demographics, Trends, and Network Graph Platform",
    version="1.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers
app.include_router(dashboard_router)
app.include_router(sentiment_router)
app.include_router(trends_router)
app.include_router(demographics_router)
app.include_router(network_router)

# WebSocket Real-Time Stream
@app.websocket("/ws/live-stream")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive & accept incoming ping/commands
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception:
        manager.disconnect(websocket)

# Static Frontend Files
if (FRONTEND_DIR / "static").exists():
    app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR / "static")), name="static")

@app.api_route("/", methods=["GET", "HEAD"])
def serve_index():
    index_file = FRONTEND_DIR / "index.html"
    if index_file.exists():
        return FileResponse(str(index_file))
    return JSONResponse({"message": f"{settings.app_name} API is operational", "docs": "/docs"})

@app.api_route("/dashboard", methods=["GET", "HEAD"])
def serve_dashboard():
    index_file = FRONTEND_DIR / "index.html"
    if index_file.exists():
        return FileResponse(str(index_file))
    return FileResponse(str(FRONTEND_DIR / "index.html"))

@app.get("/health")
def health_check():
    return {"status": "ok", "app": settings.app_name, "version": "1.0.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=settings.host, port=settings.port, reload=True)
