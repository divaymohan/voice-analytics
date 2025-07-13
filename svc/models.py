import uuid
from sqlalchemy import Column, String, Text, DateTime, Enum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import Mapped
from sqlalchemy.ext.mutable import MutableDict
from svc.db import Base
import enum

class RequestStatus(str, enum.Enum):
    pending = "pending"
    processing = "processing"
    done = "done"
    error = "error"

class TranscriptionRequest(Base):
    __tablename__ = "transcription_requests"

    request_id: Mapped[str] = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    filename: Mapped[str] = Column(String(256), nullable=False)
    status: Mapped[str] = Column(Enum(RequestStatus), default=RequestStatus.pending, nullable=False)
    created_at: Mapped[str] = Column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[str] = Column(DateTime(timezone=True), onupdate=func.now())
    result: Mapped[dict] = Column(MutableDict.as_mutable(JSONB), nullable=True)
    error: Mapped[str] = Column(Text, nullable=True) 