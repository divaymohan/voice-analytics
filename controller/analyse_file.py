from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks, Depends
from typing import Dict, Any
import sys
import os
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from svc.db import AsyncSessionLocal
from svc.models import TranscriptionRequest, RequestStatus, User, Organization
from svc.analyse_file_svc import AnalyseFileService
from svc.auth_utils import get_current_user

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
            transcript = result['results']['channels'][0]['alternatives'][0]['transcript']
            req.transcript = transcript
            review_result = await analyse_service.review_transcript(req.transcript, request_id=request_id)
            req.result = review_result.get("result")
            req.error = None
            req.status = RequestStatus.done
        except Exception as e:
            req.status = RequestStatus.error
            req.error = str(e)
        await session.commit()

@router.post("/transcribe", response_model=Dict[str, Any])
async def transcribe_audio_file(
    background_tasks: BackgroundTasks,
    audio_file: UploadFile = File(..., description="Audio file to transcribe"),
    current_user=Depends(get_current_user)
):
    request_id = str(uuid.uuid4())
    async with AsyncSessionLocal() as session:
        req = TranscriptionRequest(
            request_id=request_id,
            filename=audio_file.filename,
            status=RequestStatus.pending,
            created_by=current_user.id,
            organization_id=current_user.organization_id,
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
            return {"request_id": request_id, "result": req.result}
        elif req.status == RequestStatus.error:
            return {"request_id": request_id, "error": req.error}
        else:
            return {"request_id": request_id, "status": req.status}

@router.get("/org/{org_id}/transcripts")
async def get_org_transcripts(org_id: str, current_user: User = Depends(get_current_user)):
    # Only org owner can access
    if not current_user.is_org_owner or str(current_user.organization_id) != org_id:
        raise HTTPException(status_code=403, detail="Not authorized")
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(TranscriptionRequest, User)
            .where(TranscriptionRequest.organization_id == org_id)
            .join(User, TranscriptionRequest.created_by == User.id)
        )
        transcripts = [
            {
                "request_id": str(t.request_id),
                "filename": t.filename,
                "status": t.status,
                "created_at": t.created_at,
                "user": {
                    "id": str(u.id),
                    "name": u.name,
                    "email": u.email
                }
            }
            for t, u in result.all()
        ]
        return transcripts

@router.get("/user/transcripts")
async def get_user_transcripts(current_user: User = Depends(get_current_user)):
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(TranscriptionRequest)
            .where(TranscriptionRequest.created_by == current_user.id)
        )
        transcripts = [
            {
                "request_id": str(t.request_id),
                "filename": t.filename,
                "status": t.status,
                "created_at": t.created_at
            }
            for t in result.scalars().all()
        ]
        return transcripts

@router.delete("/transcript/{request_id}")
async def soft_delete_transcript(request_id: str, current_user: User = Depends(get_current_user)):
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(TranscriptionRequest)
            .where(TranscriptionRequest.request_id == request_id)
        )
        transcript = result.scalar_one_or_none()
        if not transcript:
            raise HTTPException(status_code=404, detail="Transcript not found")
        # Only creator or org owner can delete
        is_owner = current_user.is_org_owner and (current_user.organization_id == transcript.organization_id)
        is_creator = (transcript.created_by == current_user.id)
        if not (is_owner or is_creator):
            raise HTTPException(status_code=403, detail="Not authorized to delete this transcript")
        # Soft delete: mark status as 'deleted'
        transcript.status = "deleted"
        await session.commit()
        return {"message": "Transcript deleted (soft)"}
        
