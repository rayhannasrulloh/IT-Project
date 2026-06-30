import uuid
from datetime import datetime
from sqlalchemy import Column, String, ForeignKey, DateTime, Integer, Text
from sqlalchemy.orm import relationship
from app.core.database import Base

class Feedback(Base):
    __tablename__ = "feedback"

    feedback_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    message_id = Column(String, ForeignKey("messages.message_id"), nullable=True)  # for frontend compatibility
    conversation_id = Column(String, ForeignKey("conversations.conversation_id"), nullable=False)
    user_id = Column(String, ForeignKey("profiles.id"), nullable=False)
    rating = Column(Integer, nullable=False)  # 1 to 5
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    message = relationship("Message", back_populates="feedbacks")
    user = relationship("Profile")
