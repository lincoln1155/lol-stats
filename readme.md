# LOL Stats — League of Legends Match Tracker & AI Coach

<div align="center">

**A full-stack web application** that tracks League of Legends match history and provides real-time AI coaching powered by Google Gemini.

🔗 **[Live Demo](https://lolstats-64cbc4-lol-stats.guaracloud.com/)**

</div>

---

## Overview

LOL Stats fetches, caches, and analyzes League of Legends match data through the Riot Games API. Players can search any Riot ID to view detailed match history — including champions, items, spells, runes, KDA, and team compositions — and then ask an AI-powered coach for personalized analysis based on their recent performance.

The application follows a **distributed microservice architecture**, with the frontend and backend deployed independently and connected to managed cloud databases.

## Features

- **Dynamic Player Profiles** — Search any player by Riot ID across multiple regions (BR, NA, EUW, KR). Profiles display rank, tier, LP, and win/loss stats via the League-V4 API.
- **Detailed Match History** — Each match card shows champion played, summoner spells, runes (primary keystone + secondary tree), full item builds, KDA, CS, game duration, and all 10 participants with clickable links to their profiles.
- **AI Coach (Gemini 2.5 Flash)** — An integrated chat panel where players can ask for data-driven coaching. The LLM receives full match context (KDA, CS/min, gold, damage, vision score, items resolved to names via Data Dragon, ally/enemy compositions) and responds with actionable analysis. Includes strict guardrails against off-topic usage and prompt injection.
- **High-Performance Async Backend** — Concurrent API calls using `aiohttp` + `asyncio` with semaphore-based rate limiting (10 concurrent requests). Matches are fetched in parallel, not sequentially.
- **Multi-Layer Caching** — Redis caches search results at the edge for instant repeat queries. PostgreSQL persists match data permanently — once downloaded, a match is never re-fetched from Riot.
- **Shareable URLs** — Dynamic routing via Next.js App Router (`/[region]/[riotId]`). Every player profile has a permanent, bookmarkable URL.
- **CI/CD Pipeline** — GitHub Actions workflow validates frontend builds on every push and automates deployment.

## Architecture

```
┌─────────────────────┐     ┌──────────────────────┐
│   Next.js Frontend  │────▶│   FastAPI Backend     │
│   (GuaraCloud)      │     │   (Render)            │
└─────────────────────┘     └──────┬───────┬────────┘
                                   │       │
                            ┌──────▼──┐ ┌──▼────────┐
                            │  Redis  │ │ PostgreSQL │
                            │(Upstash)│ │ (Supabase) │
                            └─────────┘ └────────────┘
                                   │
                            ┌──────▼──────────┐
                            │  Riot Games API  │
                            │  Google Gemini   │
                            │  Data Dragon CDN │
                            └─────────────────┘
```

## Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| **Frontend** | Next.js 15 (App Router), React 19, TypeScript, Tailwind CSS | Server-side routing, component architecture, responsive UI |
| **Backend** | Python 3.12, FastAPI, Uvicorn | Async REST API with automatic OpenAPI docs |
| **Database** | PostgreSQL (Supabase), SQLAlchemy + asyncpg | Persistent match storage with async ORM |
| **Cache** | Redis (Upstash) | Edge caching for search results and API quota optimization |
| **AI** | Google Gemini 2.5 Flash (`google-genai` SDK) | LLM-based coaching with context injection and model fallback |
| **External APIs** | Riot Games API (Account-V1, Match-V5, League-V4), Data Dragon, Community Dragon | Player data, match history, ranked info, game assets |
| **DevOps** | Docker, Docker Compose, GitHub Actions CI/CD | Containerized local dev, automated build validation |
| **Hosting** | GuaraCloud (frontend), Render (backend), Supabase, Upstash | Distributed PaaS deployment |

## Project Structure

```
riot_api_project/
├── app/                          # Backend (FastAPI)
│   ├── main.py                   # App entrypoint, lifespan, CORS, router registration
│   ├── database.py               # Async SQLAlchemy engine + session factory
│   ├── models.py                 # ORM models (Match)
│   ├── schemas.py                # Pydantic validation schemas
│   ├── utils.py                  # Riot API request helper with error handling
│   ├── routers/
│   │   ├── matches.py            # /matches/{region}/{riotId} endpoint
│   │   └── chat.py               # /chat/{region}/{riotId} endpoint
│   └── services/
│       ├── riot_service.py       # Riot API integration, match parsing, region routing
│       └── llm_service.py        # Gemini integration, prompt engineering, item resolution
├── frontend/                     # Frontend (Next.js)
│   ├── Dockerfile                # Production-optimized standalone build
│   ├── src/
│   │   ├── app/
│   │   │   ├── page.tsx          # Home / search page
│   │   │   ├── layout.tsx        # Root layout with footer
│   │   │   ├── globals.css       # Design tokens and theme
│   │   │   └── [region]/
│   │   │       └── [riotId]/
│   │   │           └── page.tsx  # Dynamic dashboard (profile + matches + AI chat)
│   │   └── components/
│   │       ├── MatchCard.tsx      # Match history card with teams, items, runes
│   │       └── PlayerProfile.tsx  # Player rank and stats display
├── Dockerfile.backend            # Backend container (Python 3.12)
├── docker-compose.yml            # Local development (4-service stack)
├── .github/workflows/
│   └── deploy.yml                # CI/CD pipeline
└── requirements.txt              # Python dependencies
```

## Local Development

### Prerequisites
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running
- A [Riot API Key](https://developer.riotgames.com/)
- A [Gemini API Key](https://aistudio.google.com/apikey)

### Setup

1. Clone the repository:
```bash
git clone https://github.com/lincoln1155/riot_api_project.git
cd riot_api_project
```

2. Create a `.env` file in the root directory:
```env
RIOT_API_KEY=RGAPI-your-key-here
GEMINI_API_KEY=your-gemini-key-here

DB_USER=postgres
DB_PASSWORD=123456
DB_NAME=riot_db
DATABASE_URL=postgresql+asyncpg://postgres:123456@db:5432/riot_db
REDIS_URL=redis://redis:6379/0
```

3. Start all services:
```bash
docker compose up -d
```

4. Access the application:
  - **Frontend:** http://localhost:3000
  - **Backend API:** http://localhost:8000
  - **API Docs (Swagger):** http://localhost:8000/docs

## Technical Highlights

### Async-First Architecture
The entire backend is built on Python's `asyncio` runtime. API calls to Riot are dispatched concurrently using `aiohttp` with a semaphore-based rate limiter, reducing data fetch times by up to 10x compared to sequential requests.

### Graceful Degradation
If the Riot League-V4 API returns errors for ranked data, the system falls back to displaying "UNRANKED" instead of crashing the entire page. The AI model system uses automatic fallback from `gemini-2.5-flash` to `gemini-2.0-flash` with exponential backoff on 429/503 errors.

### LLM Prompt Engineering
The AI Coach uses a carefully crafted system prompt with strict behavioral guardrails (no off-topic responses, no toxicity, no prompt injection). Match data is pre-processed to resolve item IDs to human-readable names via Data Dragon before being injected as context, ensuring the LLM can reference specific items by name.

### Region Routing Abstraction
Riot's API uses two different region systems: platform regions (br1, na1, euw1) for ranked/summoner data and continental regions (americas, europe, asia) for account/match data. This mapping is fully abstracted in `riot_service.py`.

---

<div align="center">

Made by [Lincoln](https://github.com/lincoln1155)

</div>
