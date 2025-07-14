from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from sqlalchemy.future import select
from svc.db import AsyncSessionLocal
from svc.models import User, Organization
from svc.auth_utils import hash_password, get_current_user
import uuid

router = APIRouter(prefix="/orgs", tags=["Organization"])

class InviteUserRequest(BaseModel):
    name: str
    email: EmailStr
    password: str

async def get_org_owner_user(current_user: User, org_id: str):
    if not current_user.is_org_owner or str(current_user.organization_id) != org_id:
        raise HTTPException(status_code=403, detail="Not authorized")
    return current_user

@router.get("/{org_id}")
async def get_org(org_id: str, current_user: User = Depends(get_current_user)):
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Organization).where(Organization.id == org_id))
        org = result.scalar_one_or_none()
        if not org:
            raise HTTPException(status_code=404, detail="Organization not found")
        return {"id": str(org.id), "name": org.name, "owner_id": str(org.owner_id)}

@router.get("/{org_id}/users")
async def list_org_users(org_id: str, current_user: User = Depends(get_current_user)):
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User).where(User.organization_id == org_id))
        users = result.scalars().all()
        return [{"id": str(u.id), "name": u.name, "email": u.email, "is_org_owner": u.is_org_owner} for u in users]

@router.post("/{org_id}/invite")
async def invite_user(org_id: str, data: InviteUserRequest, current_user: User = Depends(get_current_user)):
    owner = await get_org_owner_user(current_user, org_id)
    async with AsyncSessionLocal() as session:
        # Check if user exists
        result = await session.execute(select(User).where(User.email == data.email))
        if result.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Email already registered")
        user = User(
            id=uuid.uuid4(),
            name=data.name,
            email=data.email,
            password_hash=hash_password(data.password),
            is_org_owner=False,
            organization_id=org_id,
        )
        session.add(user)
        await session.commit()
        return {"message": f"User {data.email} invited to organization."} 
    