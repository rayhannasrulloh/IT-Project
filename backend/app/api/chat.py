from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Union, List, Any
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.profiles import Profile
from app.models.feedback import Feedback
from app.schemas.chat import (
    QueryRequest, MessageResponse, FeedbackCreate, FeedbackResponse,
    ChatResponseConversation, ChatResponseClarification, ChatResponseQueryResult
)
from app.services.chat_service import ChatService

router = APIRouter(prefix="/chat", tags=["Conversational Analyst"])

@router.post("", response_model=Union[ChatResponseConversation, ChatResponseClarification, ChatResponseQueryResult])
async def submit_chat_message(
    payload: QueryRequest,
    current_user: Profile = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Finalized API endpoint: Natural language query entry point.
    Returns: Conversation, Clarification, or Query Result JSON.
    """
    service = ChatService(db)
    try:
        res = await service.handle_message(
            user_id=current_user.id,
            query_text=payload.query_text,
            conversation_id=payload.conversation_id,
            model_provider=payload.model_provider,
            model=payload.model
        )
        
        # Format the response based on the type
        t = res["type"]
        if t == "conversation":
            return ChatResponseConversation(type="conversation", message=res["message"])
        elif t == "clarification":
            return ChatResponseClarification(type="clarification", message=res["message"], missing_fields=res.get("missing_fields"))
        elif t == "query_result":
            return ChatResponseQueryResult(
                type="query_result",
                question=res["question"],
                sql=res["sql"],
                data=res["data"],
                chart=res.get("chart")
            )
        else:
            raise HTTPException(status_code=500, detail="Unknown chat response state")
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process query: {str(e)}")


@router.post("/query", response_model=MessageResponse)
async def submit_query_compat(
    payload: QueryRequest,
    current_user: Profile = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Compatibility route matching frontend's /api/v1/chat/query.
    Processes the request and returns a full MessageResponse object.
    """
    service = ChatService(db)
    try:
        res = await service.handle_message(
            user_id=current_user.id,
            query_text=payload.query_text,
            conversation_id=payload.conversation_id,
            model_provider=payload.model_provider,
            model=payload.model
        )
        
        db_msg = res["db_message"]
        # Convert DB Message model to MessageResponse
        return MessageResponse.from_orm(db_msg)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed compatibility chat flow: {str(e)}")


@router.post("/feedback", response_model=FeedbackResponse)
async def submit_feedback(
    payload: FeedbackCreate,
    current_user: Profile = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Logs rating feedback (thumbs-up/thumbs-down) on generated answers."""
    # Find conversation id
    conversation_id = payload.conversation_id
    if not conversation_id and payload.message_id:
        # Load from message
        from app.models.messages import Message
        from sqlalchemy.future import select
        stmt = select(Message).filter_by(message_id=payload.message_id)
        msg_obj = (await db.execute(stmt)).scalar_one_or_none()
        if msg_obj:
            conversation_id = msg_obj.conversation_id
            
    if not conversation_id:
        raise HTTPException(status_code=400, detail="Either conversation_id or message_id is required")

    feedback = Feedback(
        message_id=payload.message_id,
        conversation_id=conversation_id,
        user_id=current_user.id,
        rating=payload.rating,
        comment=payload.comment
    )
    db.add(feedback)
    await db.commit()
    await db.refresh(feedback)
    return feedback
