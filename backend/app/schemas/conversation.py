from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class ConversationCreate(BaseModel):
    title: Optional[str] = Field(default="New Conversation")

class ConversationResponse(BaseModel):
    conversation_id: str
    user_id: str
    title: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
