from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.profiles import Profile
from app.schemas.chat import ProfileResponse, ProfileCreate
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.get("/me", response_model=ProfileResponse)
async def get_me(current_user: Profile = Depends(get_current_user)):
    """Retrieve the current logged-in user profile with role configuration."""
    return current_user

@router.post("/sync", response_model=ProfileResponse)
async def sync_profile(profile_data: ProfileCreate, db: AsyncSession = Depends(get_db)):
    """Synchronizes user attributes from Supabase Auth into our PostgreSQL profiles table."""
    service = AuthService(db)
    return await service.sync_profile(
        id=profile_data.id,
        email=profile_data.email,
        full_name=profile_data.full_name
    )
