from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from app.repositories.query_repository import QueryRepository
from app.models.profiles import Profile

class AuthService:
    def __init__(self, db: AsyncSession):
        self.repo = QueryRepository(db)

    async def get_profile(self, profile_id: str) -> Optional[Profile]:
        """Retrieves profile from the database."""
        return await self.repo.get_profile_by_id(profile_id)

    async def sync_profile(self, id: str, email: str, full_name: Optional[str]) -> Profile:
        """Syncs Supabase user profile attributes into local postgres."""
        existing = await self.repo.get_profile_by_id(id)
        if existing:
            existing.email = email
            if full_name:
                existing.full_name = full_name
            await self.repo.db.commit()
            await self.repo.db.refresh(existing)
            return existing
            
        # Role escalation triggers
        role = "user"
        if email.endswith("admin@cda.com") or id.startswith("admin-"):
            role = "admin"
            
        profile = Profile(
            id=id,
            email=email,
            full_name=full_name or email.split("@")[0].capitalize(),
            role=role
        )
        self.repo.db.add(profile)
        await self.repo.db.commit()
        await self.repo.db.refresh(profile)
        return profile
