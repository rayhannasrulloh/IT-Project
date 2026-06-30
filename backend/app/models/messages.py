import uuid
from datetime import datetime
from sqlalchemy import Column, String, ForeignKey, DateTime, Text, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base

class Message(Base):
    __tablename__ = "messages"

    message_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    conversation_id = Column(String, ForeignKey("conversations.conversation_id"), nullable=False)
    sender = Column(String(20), nullable=False)  # user, assistant
    content = Column(Text, nullable=False)
    generated_sql = Column(Text, nullable=True)
    sql_results = Column(JSON, nullable=True)
    visualization_config = Column(JSON, nullable=True)
    explanation = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    conversation = relationship("Conversation", back_populates="messages")
    feedbacks = relationship("Feedback", back_populates="message", cascade="all, delete-orphan")

    @property
    def role(self) -> str:
        return self.sender

    @role.setter
    def role(self, value: str):
        self.sender = value
