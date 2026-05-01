from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas import ChatRequest
from app.services.riot_service import get_full_match_data
from app.services.llm_service import format_matches_for_prompt, generate_response

router = APIRouter()

@router.post("/chat/{region}/{riot_id}")
async def chat(request: Request, region: str, riot_id: str, body: ChatRequest, db: AsyncSession = Depends(get_db)):
    if not request.app.state.genai:
        raise HTTPException(status_code=503, detail="AI chat is not configured. Set GEMINI_API_KEY in .env")

    session = request.app.state.session
    matches, puuid = await get_full_match_data(session, region, riot_id, db)

    if not matches:
        raise HTTPException(status_code=404, detail="No match data found for this player")

    context = format_matches_for_prompt(matches, puuid)
    response = await generate_response(
        client=request.app.state.genai,
        question=body.message,
        matches_context=context,
        chat_history=body.history,
    )

    return {"response": response}
