import os
import aiohttp
import redis.asyncio as redis
from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from dotenv import load_dotenv
from contextlib import asynccontextmanager
from google import genai

from app.database import Base, engine
from app.services.llm_service import load_item_names
from app.routers import matches, chat

load_dotenv(".env")
REDIS_URL = os.environ.get("REDIS_URL")
GEMINI_KEY = os.environ.get("GEMINI_API_KEY")

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.session = aiohttp.ClientSession()
    app.state.redis = redis.from_url(REDIS_URL, decode_responses=True)
    app.state.genai = genai.Client(api_key=GEMINI_KEY) if GEMINI_KEY else None
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    await load_item_names()

    yield
    await app.state.session.close()
    await app.state.redis.close()

app = FastAPI(lifespan=lifespan)

STATIC_DIR = Path(__file__).resolve().parent.parent / "static"
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

app.include_router(matches.router)
app.include_router(chat.router)

@app.get("/")
async def root():
    return FileResponse(str(STATIC_DIR / "index.html"))

@app.get("/search/{region}/{riot_id}")
async def search_page(region: str, riot_id: str):
    return FileResponse(str(STATIC_DIR / "index.html"))