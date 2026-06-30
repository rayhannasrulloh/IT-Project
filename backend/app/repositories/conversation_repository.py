from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import delete
from typing import List, Optional
from datetime import datetime
from app.models.conversations import Conversation
from app.models.messages import Message
from app.models.conversation_context import ConversationContext

class ConversationRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, user_id: str, title: str) -> Conversation:
        conversation = Conversation(user_id=user_id, title=title)
        self.db.add(conversation)
        await self.db.commit()
        await self.db.refresh(conversation)
        return conversation

    async def get_by_id(self, conversation_id: str) -> Optional[Conversation]:
        stmt = select(Conversation).filter_by(conversation_id=conversation_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all_by_user(self, user_id: str) -> List[Conversation]:
        stmt = select(Conversation).filter_by(user_id=user_id).order_by(Conversation.updated_at.desc())
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def delete(self, conversation_id: str) -> bool:
        stmt = delete(Conversation).filter_by(conversation_id=conversation_id)
        result = await self.db.execute(stmt)
        await self.db.commit()
        return (result.rowcount or 0) > 0

    async def add_message(
        self,
        conversation_id: str,
        role: str,  # maps to sender column
        content: str,
        generated_sql: Optional[str] = None,
        sql_results: Optional[dict] = None,
        visualization_config: Optional[dict] = None,
        explanation: Optional[str] = None
    ) -> Message:
        message = Message(
            conversation_id=conversation_id,
            sender=role,
            content=content,
            generated_sql=generated_sql,
            sql_results=sql_results,
            visualization_config=visualization_config,
            explanation=explanation
        )
        self.db.add(message)
        
        # Touch conversation updated_at
        stmt = select(Conversation).filter_by(conversation_id=conversation_id)
        res = await self.db.execute(stmt)
        conv = res.scalar_one_or_none()
        if conv:
            conv.updated_at = datetime.utcnow()
            
        await self.db.commit()
        await self.db.refresh(message)
        return message

    async def get_messages(self, conversation_id: str) -> List[Message]:
        stmt = select(Message).filter_by(conversation_id=conversation_id).order_by(Message.created_at.asc())
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    # --- Conversation Context Methods ---
    async def get_context(self, conversation_id: str) -> Optional[ConversationContext]:
        stmt = select(ConversationContext).filter_by(conversation_id=conversation_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def create_context(
        self,
        conversation_id: str,
        pending_intent: Optional[str] = None,
        missing_fields: Optional[List[str]] = None,
        collected_data: Optional[dict] = None
    ) -> ConversationContext:
        context = ConversationContext(
            conversation_id=conversation_id,
            pending_intent=pending_intent,
            missing_fields=missing_fields or [],
            collected_data=collected_data or {}
        )
        self.db.add(context)
        await self.db.commit()
        await self.db.refresh(context)
        return context

    async def update_context(
        self,
        conversation_id: str,
        pending_intent: Optional[str],
        missing_fields: List[str],
        collected_data: dict
    ) -> Optional[ConversationContext]:
        context = await self.get_context(conversation_id)
        if context:
            context.pending_intent = pending_intent
            context.missing_fields = missing_fields
            context.collected_data = collected_data
            context.updated_at = datetime.utcnow()
            await self.db.commit()
            await self.db.refresh(context)
        else:
            context = await self.create_context(conversation_id, pending_intent, missing_fields, collected_data)
        return context

    async def delete_context(self, conversation_id: str) -> bool:
        stmt = delete(ConversationContext).filter_by(conversation_id=conversation_id)
        result = await self.db.execute(stmt)
        await self.db.commit()
        return (result.rowcount or 0) > 0
