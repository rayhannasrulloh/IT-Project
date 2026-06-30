import uuid
from datetime import datetime
from sqlalchemy import Column, String, ForeignKey, DateTime, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base

class ConversationContext(Base):
    __tablename__ = "conversation_context"

    context_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    conversation_id = Column(String, ForeignKey("conversations.conversation_id"), nullable=False)
    pending_intent = Column(String(100), nullable=True)
    missing_fields = Column(JSON, nullable=False, default=list)  # Stored as JSON list of strings
    collected_data = Column(JSON, nullable=False, default=dict)   # Stored as JSON dictionary
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    conversation = relationship("Conversation", back_populates="contexts")
