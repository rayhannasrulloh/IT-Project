from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.profiles import Profile
from app.schemas.conversation import ConversationResponse, ConversationCreate
from app.schemas.chat import MessageResponse
from app.repositories.conversation_repository import ConversationRepository

router = APIRouter(prefix="/chat/conversations", tags=["Conversations Management"])

@router.get("", response_model=List[ConversationResponse])
async def list_conversations(
    current_user: Profile = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Retrieve all conversations for the current logged-in user."""
    repo = ConversationRepository(db)
    return await repo.get_all_by_user(current_user.id)


@router.post("", response_model=ConversationResponse)
async def create_conversation(
    payload: ConversationCreate,
    current_user: Profile = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Start a new data conversation thread."""
    repo = ConversationRepository(db)
    return await repo.create(user_id=current_user.id, title=payload.title)


@router.get("/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(
    conversation_id: str,
    current_user: Profile = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Retrieve details of a specific conversation session."""
    repo = ConversationRepository(db)
    conv = await repo.get_by_id(conversation_id)
    if not conv or conv.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Conversation thread not found")
    return conv


@router.delete("/{conversation_id}")
async def delete_conversation(
    conversation_id: str,
    current_user: Profile = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a conversation thread and all its messages."""
    repo = ConversationRepository(db)
    conv = await repo.get_by_id(conversation_id)
    if not conv or conv.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Conversation not found or unauthorized")
    
    success = await repo.delete(conversation_id)
    return {"success": success, "message": "Conversation deleted successfully"}


@router.get("/{conversation_id}/messages", response_model=List[MessageResponse])
async def get_messages(
    conversation_id: str,
    current_user: Profile = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Fetch complete message list history for a specific conversation session (frontend compatibility)."""
    repo = ConversationRepository(db)
    conv = await repo.get_by_id(conversation_id)
    if not conv or conv.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Conversation not found or unauthorized")
    return await repo.get_messages(conversation_id)
