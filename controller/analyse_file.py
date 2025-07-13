from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from typing import Dict, Any
import sys
import os
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from svc.db import AsyncSessionLocal
from svc.models import TranscriptionRequest, RequestStatus
from svc.analyse_file_svc import AnalyseFileService

router = APIRouter(prefix="/api/v1", tags=["Audio Analysis"])

analyse_service = AnalyseFileService()

async def process_transcription(request_id: str, file_content: bytes, filename: str):
    async with AsyncSessionLocal() as session:
        # Update status to processing
        result = await session.execute(select(TranscriptionRequest).where(TranscriptionRequest.request_id == request_id))
        req = result.scalar_one_or_none()
        if not req:
            return
        req.status = RequestStatus.processing
        await session.commit()
        try:
            result = await analyse_service.transcribe_audio_file(file_content, filename)
            result = await analyse_service.review_transcript(result['results']['channels'][0]['alternatives'][0]['transcript'])
            req.status = RequestStatus.done
            req.result = result
            req.error = None
        except Exception as e:
            req.status = RequestStatus.error
            req.error = str(e)
        await session.commit()

@router.post("/transcribe", response_model=Dict[str, Any])
async def transcribe_audio_file(
    background_tasks: BackgroundTasks,
    audio_file: UploadFile = File(..., description="Audio file to transcribe")
):
    request_id = str(uuid.uuid4())
    async with AsyncSessionLocal() as session:
        req = TranscriptionRequest(
            request_id=request_id,
            filename=audio_file.filename,
            status=RequestStatus.pending,
        )
        session.add(req)
        await session.commit()
    file_content = await audio_file.read()
    background_tasks.add_task(process_transcription, request_id, file_content, audio_file.filename)
    return {"request_id": request_id}

@router.get("/status/{request_id}")
async def get_status(request_id: str):
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(TranscriptionRequest).where(TranscriptionRequest.request_id == request_id))
        req = result.scalar_one_or_none()
        if not req:
            raise HTTPException(status_code=404, detail="Request not found")
        return {"request_id": request_id, "status": req.status}

@router.get("/result/{request_id}")
async def get_result(request_id: str):
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(TranscriptionRequest).where(TranscriptionRequest.request_id == request_id))
        req = result.scalar_one_or_none()
        if not req:
            raise HTTPException(status_code=404, detail="Request not found")
        if req.status == RequestStatus.done:
            result = await analyse_service.review_transcript(
                req.result['results']['channels'][0]['alternatives'][0]['transcript'])
            return {"request_id": request_id, "result": result}
        elif req.status == RequestStatus.error:
            return {"request_id": request_id, "error": req.error}
        else:
            return {"request_id": request_id, "status": req.status}
