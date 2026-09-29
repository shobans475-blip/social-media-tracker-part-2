# SENTINEL-AI: Social Media Intelligence & Analytics Platform

> **Smart India Hackathon (SIH) Project Architecture**  
> Real-Time Multi-Source Ingestion, NLP Sentiment, Demographics, Trends, and NetworkX Link Analysis Platform.

---

## 🏛️ System Architecture

```text
                  SOCIAL MEDIA SOURCES
        ┌──────────┬──────────┬──────────┐
        │    X     │ Telegram │ Instagram│
        └────┬─────┴─────┬────┴────┬─────┘
             │           │         │
             └───────────┼─────────┘
                         ▼
                ┌─────────────────┐
                │ DATA INGESTION  │
                │ Python Workers  │
                └────────┬────────┘
                         ▼
                ┌─────────────────┐
                │ DATA PROCESSING │
                │ Clean / Detect  │
                │ Language / NLP  │
                └────────┬────────┘
                         ▼
       ┌─────────────────┼──────────────────┐
       ▼                 ▼                  ▼
┌─────────────┐   ┌──────────────┐   ┌──────────────┐
│  SENTIMENT  │   │ DEMOGRAPHICS │   │    TRENDS    │
│ NLP Model   │   │ Aggregate AI │   │ Topic Model  │
└──────┬──────┘   └──────┬───────┘   └──────┬───────┘
       │                 │                  │
       └─────────────────┼──────────────────┘
                         ▼
                ┌─────────────────┐
                │ LINK ANALYSIS   │
                │ NetworkX / Graph│
                └────────┬────────┘
                         ▼
                ┌─────────────────┐
                │ PostgreSQL DB   │
                │ + Redis Cache   │
                └────────┬────────┘
                         ▼
                ┌─────────────────┐
                │   FastAPI       │
                │ REST + WebSocket│
                └────────┬────────┘
                         ▼
                ┌─────────────────┐
                │   DASHBOARD     │
                │ React / HTML    │
                └─────────────────┘
```

---

## 📂 Project Directory Structure

```text
social-media-ai/
│
├── backend/
│   ├── main.py                     # FastAPI entry point, WebSocket broadcast, background stream
│   ├── requirements.txt            # Python dependencies
│   ├── .env                        # Environment configuration and API keys
│   │
│   ├── config/
│   │   └── settings.py             # Pydantic environment configuration
│   │
│   ├── api/
│   │   ├── routes_dashboard.py     # Summary KPIs, enriched live feed, event injection
│   │   ├── routes_sentiment.py     # Sentiment metrics & interactive live NLP sandbox
│   │   ├── routes_trends.py        # TF-IDF topic clusters & hashtag velocity
│   │   ├── routes_demographics.py  # Age cohorts, gender, regional geo hubs, bot detection
│   │   └── routes_network.py       # Directed NetworkX graph, PageRank & influencers
│   │
│   ├── collectors/
│   │   ├── twitter.py              # X/Twitter collector (Hybrid: streaming generator + v2 API)
│   │   ├── telegram.py             # Telegram channel & broadcast collector
│   │   ├── instagram.py            # Instagram media & creator engagement collector
│   │   └── youtube.py              # YouTube video & comment telemetry collector
│   │
│   ├── models/
│   │   ├── sentiment.py            # Multilingual sentiment, toxicity & misinformation model
│   │   ├── demographics.py         # Age, gender, regional and bot scoring heuristic models
│   │   ├── trends.py               # TF-IDF vectorizer & hashtag velocity tracker
│   │   └── network.py              # NetworkX graph builder, PageRank, community detection
│   │
│   ├── services/
│   │   ├── preprocessing.py        # Tokenizer, stopword removal, entity extraction
│   │   ├── sentiment_service.py    # Sentiment aggregations & alert triggers
│   │   ├── demographic_service.py  # Cohort aggregation & bot analysis
│   │   ├── trend_service.py        # Emerging hashtag & cluster ranking
│   │   └── network_service.py      # Subgraph export for 2D force-directed canvas
│   │
│   ├── database/
│   │   ├── database.py             # SQLAlchemy engine (SQLite zero-dependency + PostgreSQL)
│   │   └── schemas.py              # ORM models (exact 'posts' schema + users, sentiments)
│   │
│   └── utils/
│       ├── language.py             # Multilingual script & Hinglish detection
│       └── helpers.py              # Text cleaning, extraction & formatting utilities
│
├── frontend/
│   ├── index.html                  # Glassmorphic intelligence command center
│   └── static/
│       ├── css/
│       │   └── style.css           # Modern dark-mode responsive design system
│       └── js/
│           ├── app.js              # WebSocket consumer, Chart.js integrations, UI logic
│           └── network_graph.js    # Interactive 2D Canvas force-directed graph engine
│
├── data/
│   ├── sample_social_data.json     # Multilingual benchmark dataset (X, Telegram, IG, YT)
│   └── social_media.db             # Auto-generated SQLite database
│
└── README.md
```

---

## 🗄️ Database Schema

### `posts` Table (Exact Specification)
| Column | Type | Description |
|---|---|---|
| `id` | VARCHAR(64) | Unique post identifier (Primary Key) |
| `platform` | VARCHAR(32) | Source platform (`twitter`, `telegram`, `instagram`, `youtube`) |
| `platform_post_id` | VARCHAR(64) | Native platform post/message ID |
| `user_id` | VARCHAR(64) | Author ID (Foreign Key to users) |
| `text` | TEXT | Post content |
| `language` | VARCHAR(16) | Detected language code (`en`, `hi`, `hinglish`, `ta`, etc.) |
| `created_at` | DATETIME | Post publication timestamp |
| `likes` | INTEGER | Likes / positive reactions |
| `shares` | INTEGER | Retweets, forwards, or shares |
| `comments` | INTEGER | Reply count |
| `parent_post_id` | VARCHAR(64) | Repost/reply relationship pointer for network linking |

---

## 🚀 Quickstart: Running Locally

### 1. Requirements
Ensure Python 3.10+ is installed:
```bash
python --version
```

### 2. Start the Platform
Navigate to the project backend directory and run:
```bash
cd "d:\sih social media\social-media-ai\backend"
python main.py
```

Or run via Uvicorn:
```bash
uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

### 3. Open in Browser
- **Interactive Dashboard:** [http://localhost:8000/](http://localhost:8000/)
- **Swagger Interactive API Documentation:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **Live WebSocket Feed:** `ws://localhost:8000/ws/live-stream`

---

## 💡 Key Features for Hackathon Judges

1. **2D Force-Directed Network Graph (HTML5 Canvas)**
   - Visualizes nodes (influencers, bots, public figures) and links (replies, retweets, forwards).
   - Node size dynamically maps to **PageRank centrality**.
   - Colors map to **Community clusters** (Tech, Civic, Eco, Threat).
   - Pan, zoom, drag nodes, and hover for detailed telemetry cards.

2. **Real-Time WebSocket Streaming**
   - Continuously ingests posts across all 4 platforms.
   - Highlights high-priority **Threat & Misinformation Alerts** with glowing rose borders.

3. **Interactive NLP Sandbox**
   - Paste any tweet or message in Hindi, Hinglish, or English.
   - Instantly calculates sentiment polarity, toxicity percentage, language, and extracts Gemini AI analysis!

4. **Demographics & Geo Breakdown**
   - Visual age cohorts (18-24, 25-34, 35-49, 50+).
   - Regional distribution across major Indian hubs (Karnataka, Maharashtra, Delhi NCR, Tamil Nadu, etc.).
   - Coordinated bot activity detection.

5. **Demo Event Injection Buttons**
   - Click **`+ Threat Event`** to inject a high-risk cyber scam alert.
   - Click **`+ Viral Event`** to inject a trending tech breakthrough.
