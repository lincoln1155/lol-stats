import os
import aiohttp
import redis.asyncio as redis
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(matches.router)
app.include_router(chat.router)