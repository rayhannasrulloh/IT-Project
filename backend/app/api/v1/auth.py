from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.core.database import get_db
from app.core.security import get_current_user
from app.domain.models import Profile
from app.api.schemas import ProfileResponse, ProfileCreate
from app.core.limiter import limiter

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.get("/me", response_model=ProfileResponse)
@limiter.limit("30/minute")
async def get_me(request: Request, current_user: Profile = Depends(get_current_user)):
    """Retrieve the current logged-in user profile with role configuration."""
    return current_user

@router.post("/sync", response_model=ProfileResponse)
@limiter.limit("10/minute")
async def sync_profile(
    request: Request,
    response: Response,
    profile_data: ProfileCreate,
    current_user: Profile = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Synchronizes user attributes from Supabase Auth into our PostgreSQL profiles table.
    Requires an authenticated bearer token. Users can only sync their own profile.
    Sets HttpOnly session cookie cda_access_token.
    """
    if current_user.role != "admin" and current_user.id != profile_data.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Operation not permitted. You can only synchronize your own profile."
        )

    stmt = select(Profile).filter_by(id=profile_data.id)
    result = await db.execute(stmt)
    existing_profile = result.scalar_one_or_none()

    if existing_profile:
        # Update email/name if changed
        existing_profile.email = profile_data.email
        if profile_data.full_name:
            existing_profile.full_name = profile_data.full_name
        await db.commit()
        await db.refresh(existing_profile)
        profile = existing_profile
    else:
        # New profile creation under current_user's verified role
        profile = Profile(
            id=profile_data.id,
            email=profile_data.email,
            full_name=profile_data.full_name or profile_data.email.split("@")[0].capitalize(),
            role=current_user.role
        )
        db.add(profile)
        await db.commit()
        await db.refresh(profile)

    # Generate token payload signed with Supabase JWT secret using server-verified role
    from jose import jwt
    from datetime import datetime, timedelta
    from app.core.config import settings

    payload = {
        "sub": profile.id,
        "email": profile.email,
        "role": "authenticated",
        "aud": "authenticated",
        "app_metadata": {
            "provider": "email",
            "providers": ["email"],
            "role": profile.role
        },
        "exp": datetime.utcnow() + timedelta(days=7)
    }
    token = jwt.encode(payload, settings.SUPABASE_JWT_SECRET, algorithm="HS256")

    # Set secure HttpOnly session cookie
    response.set_cookie(
        key="cda_access_token",
        value=token,
        httponly=True,
        samesite="lax",
        secure=(settings.ENVIRONMENT != "development"),
        max_age=7 * 24 * 60 * 60
    )

    response_data = ProfileResponse.model_validate(profile)
    response_data.token = token
    return response_data

@router.post("/logout")
async def logout(response: Response):
    """Logs out the current user session by clearing the HttpOnly session cookie."""
    response.delete_cookie(
        key="cda_access_token",
        httponly=True,
        samesite="lax",
        secure=(settings.ENVIRONMENT != "development")
    )
    return {"status": "success", "message": "Successfully logged out."}


