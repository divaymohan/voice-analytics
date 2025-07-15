import uuid
from sqlalchemy import Column, String, Text, DateTime, Enum, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID, JSONB, UUID as PG_UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import Mapped, relationship
from sqlalchemy.ext.mutable import MutableDict
from svc.db import Base
import enum

class RequestStatus(str, enum.Enum):
    pending = "pending"
    processing = "processing"
    done = "done"
    deleted = "deleted"
    error = "error"

class TranscriptionRequest(Base):
    __tablename__ = "transcription_requests"

    request_id: Mapped[str] = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    filename: Mapped[str] = Column(String(256), nullable=False)
    transcript: Mapped[str] = Column(Text, nullable=True)
    status: Mapped[str] = Column(Enum(RequestStatus), default=RequestStatus.pending, nullable=False)
    created_at: Mapped[str] = Column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[str] = Column(DateTime(timezone=True), onupdate=func.now())
    result: Mapped[dict] = Column(MutableDict.as_mutable(JSONB), nullable=True)
    error: Mapped[str] = Column(Text, nullable=True)
    created_by: Mapped[str] = Column(PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    organization_id: Mapped[str] = Column(PG_UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=True)

class Organization(Base):
    __tablename__ = "organizations"
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    name = Column(String(128), nullable=False, unique=True)
    owner_id = Column(PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    users = relationship(
        "User",
        back_populates="organization",
        foreign_keys="User.organization_id"
    )
    owner = relationship(
        "User",
        foreign_keys="[Organization.owner_id]",
        uselist=False
    )

class User(Base):
    __tablename__ = "users"
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    name = Column(String(128), nullable=False)
    email = Column(String(128), nullable=False, unique=True)
    password_hash = Column(String(256), nullable=False)
    is_org_owner = Column(Boolean, default=False)
    organization_id = Column(PG_UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=True)
    organization = relationship(
        "Organization",
        back_populates="users",
        foreign_keys="[User.organization_id]"
    ) 