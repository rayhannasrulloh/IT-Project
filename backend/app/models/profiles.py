from datetime import datetime
from sqlalchemy import Column, String, DateTime
from sqlalchemy.orm import relationship
from app.core.database import Base

class Profile(Base):
    __tablename__ = "profiles"

    id = Column(String, primary_key=True, index=True)  # UUID or String representation
    email = Column(String, unique=True, nullable=False, index=True)
    full_name = Column(String, nullable=True)
    role = Column(String, default="user", nullable=False)  # admin, user
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    conversations = relationship("Conversation", back_populates="user", cascade="all, delete-orphan")
    query_logs = relationship("QueryLog", back_populates="user", cascade="all, delete-orphan")
