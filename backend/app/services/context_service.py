from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from app.repositories.conversation_repository import ConversationRepository
from app.models.conversation_context import ConversationContext

class ContextService:
    def __init__(self, db: AsyncSession):
        self.repo = ConversationRepository(db)

    async def get_or_create_context(self, conversation_id: str) -> ConversationContext:
        """Retrieves an existing conversation context or creates a new one."""
        ctx = await self.repo.get_context(conversation_id)
        if not ctx:
            ctx = await self.repo.create_context(conversation_id)
        return ctx

    async def update_context(
        self,
        conversation_id: str,
        pending_intent: Optional[str],
        missing_fields: List[str],
        collected_data: dict
    ) -> ConversationContext:
        """Saves current state variables for ambiguity checks."""
        return await self.repo.update_context(
            conversation_id=conversation_id,
            pending_intent=pending_intent,
            missing_fields=missing_fields,
            collected_data=collected_data
        )

    async def clear_context(self, conversation_id: str) -> bool:
        """Resets the context table for a conversation thread."""
        return await self.repo.delete_context(conversation_id)
