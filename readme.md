# Riot AI Coach 🎮🤖

A high-performance, full-stack web application that fetches, caches, and analyzes League of Legends match data. It uses the **Riot Games API** to gather player statistics and integrates with **Google Gemini (LLM)** to provide personalized, data-driven coaching insights based on the player's recent performance.

## ✨ Key Features

1. **High-Concurrency Data Retrieval:** Uses `asyncio` and `aiohttp` to concurrently fetch match data from Riot's servers, drastically reducing load times. Rate-limiting is handled smoothly using Semaphores.
2. **Intelligent Caching:** Implements **Redis** to cache user searches at the edge, saving API quota and making repeat queries instantaneous.
3. **Persistent Storage:** Uses **PostgreSQL** to permanently store match data. Once a match is downloaded, it's never requested from Riot again.
4. **AI Coach Analysis:** Integrates **Google Gemini 2.5 Flash** to act as a League of Legends coach.
   - Translates raw Item IDs into actual Item Names via **Data Dragon**.
   - Uses *Context Injection* to feed KDA, CS, Gold, and Vision data to the LLM.
   - Includes strict *Guardrails* to prevent off-topic interactions and enforce a professional, data-centric coaching persona.
5. **Modern Frontend UI:** A clean, responsive, and dynamic interface built with vanilla HTML/CSS/JS. It features a split layout with a Match History list and a conversational Chat Panel.

## 🛠️ Technology Stack

* **Backend:** Python 3.13, FastAPI (Clean Architecture: Routers & Services)
* **Database:** PostgreSQL (with SQLAlchemy AsyncSession)
* **Cache:** Redis
* **AI Integration:** `google-genai` (Gemini 2.5 Flash)
* **Frontend:** Vanilla HTML5, CSS3, JavaScript
* **DevOps:** Docker, Docker Compose

## 📋 Setup & Installation

### 1. Prerequisites
- Docker Desktop installed and running.
- A **Riot API Key** from the [Riot Developer Portal](https://developer.riotgames.com/).
- A **Gemini API Key** from [Google AI Studio](https://aistudio.google.com/).

### 2. Configuration
Create a `.env` file in the root directory of the project to store your credentials:
```env
# Riot API
RIOT_API_KEY=RGAPI-your-key-here

# Database (PostgreSQL)
DB_USER=postgres
DB_PASSWORD=123456
DB_NAME=riot_db
DATABASE_URL=postgresql+asyncpg://postgres:123456@db:5432/riot_db

# Cache (Redis)
REDIS_URL=redis://redis:6379/0

# Google Gemini
GEMINI_API_KEY=AIzaSy...your-key-here
CHAT_DEBUG=true
```

### 3. Running the project
You don't need to install Python or database servers locally. Just use Docker:
```bash
docker compose up -d
```
*Docker will automatically build the images, set up the PostgreSQL database, initialize Redis, and start the FastAPI server.*

Once the containers are running, access the application at:
👉 `http://localhost:8000`

For API documentation (Swagger UI), visit:
👉 `http://localhost:8000/docs`

## 🗺️ Roadmap & Completed Milestones

- [x] **Asynchronous Refactoring:** Replaced blocking requests with `aiohttp/asyncio` for concurrent API calls.
- [x] **Robust Error Handling:** Logic to handle Rate Limits (429) and LLM fallback (Exponential Backoff).
- [x] **Data Persistence:** Added PostgreSQL and Redis layers to minimize API usage.
- [x] **Web Framework Integration:** Transitioned the logic into a REST API using FastAPI.
- [x] **Frontend:** Built a responsive Web UI.
- [x] **AI Integration:** Added LLM-based coaching system.
- [x] **Clean Architecture:** Refactored monolithic codebase into scalable Routers and Services.
