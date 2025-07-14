from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from svc.db import AsyncSessionLocal
from svc.models import User, Organization
from svc.auth_utils import hash_password, verify_password, create_access_token, get_current_user
import uuid
import os

router = APIRouter(prefix="/auth", tags=["Auth"])

class SignupRequest(BaseModel):
    name: str
    email: EmailStr
    password: str
    organization_name: str = None  # If provided, create org and make user owner

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

@router.post("/signup")
async def signup(data: SignupRequest):
    async with AsyncSessionLocal() as session:
        # Check if user exists
        result = await session.execute(select(User).where(User.email == data.email))
        if result.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Email already registered")
        org_id = None
        is_org_owner = False
        if data.organization_name:
            # Create organization
            org = Organization(
                id=uuid.uuid4(),
                name=data.organization_name,
            )
            session.add(org)
            await session.flush()  # get org.id
            org_id = org.id
            is_org_owner = True
        user = User(
            id=uuid.uuid4(),
            name=data.name,
            email=data.email,
            password_hash=hash_password(data.password),
            is_org_owner=is_org_owner,
            organization_id=org_id,
        )
        session.add(user)
        if is_org_owner:
            org.owner_id = user.id
        await session.commit()
        return {"message": "Signup successful"}

@router.post("/login")
async def login(data: LoginRequest):
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User).where(User.email == data.email))
        user = result.scalar_one_or_none()
        if not user or not verify_password(data.password, user.password_hash):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        token = create_access_token({"sub": str(user.id), "email": user.email})
        return {"access_token": token, "token_type": "bearer"}

@router.get("/me")
async def get_me(current_user: User = Depends(get_current_user)):
    org = None
    if current_user.organization_id:
        async with AsyncSessionLocal() as session:
            result = await session.execute(select(Organization).where(Organization.id == current_user.organization_id))
            org_obj = result.scalar_one_or_none()
            if org_obj:
                org = {"id": str(org_obj.id), "name": org_obj.name, "owner_id": str(org_obj.owner_id)}
    return {
        "user": {
            "id": str(current_user.id),
            "name": current_user.name,
            "email": current_user.email,
            "is_org_owner": current_user.is_org_owner,
            "organization_id": str(current_user.organization_id) if current_user.organization_id else None
        },
        "organization": org
    } 
    