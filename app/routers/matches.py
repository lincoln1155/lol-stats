import json
import asyncio
from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models import Match
from app.services.riot_service import get_player_dashboard_data

router = APIRouter()

@router.get("/matches/{region}/{riot_id}")
async def search_matches(request: Request, region: str, riot_id: str, db: AsyncSession = Depends(get_db)):
    session = request.app.state.session

    cache_key = f"dashboard:{region}:{riot_id.lower()}"
    cached = await request.app.state.redis.get(cache_key)
    if cached:
        return {"source": "cache", "data": json.loads(cached)}

    try:
        dashboard_data = await get_player_dashboard_data(session, region, riot_id, db)
    except Exception as e:
        # Pass HTTPExceptions through
        raise e

    await request.app.state.redis.setex(cache_key, 300, json.dumps(dashboard_data))

    return {
        "source": "api/db",
        "data": dashboard_data
    }
