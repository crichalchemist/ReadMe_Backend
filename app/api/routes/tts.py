from fastapi import APIRouter, HTTPException
from fastapi.concurrency import run_in_threadpool

from ...schemas import TTSRequest, TTSResponse
from ...services.tts import tts_service

router = APIRouter()


@router.post("/tts", response_model=TTSResponse)
async def synthesize_tts(payload: TTSRequest):
    try:
        audio_path = await run_in_threadpool(tts_service.synthesize, payload.text)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return TTSResponse(audio_path=audio_path)
