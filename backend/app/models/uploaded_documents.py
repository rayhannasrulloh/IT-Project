import uuid
from datetime import datetime
from sqlalchemy import Column, String, ForeignKey, DateTime, Integer
from sqlalchemy.orm import relationship
from app.core.database import Base

class UploadedDocument(Base):
    __tablename__ = "uploaded_documents"

    document_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("profiles.id"), nullable=False)
    filename = Column(String(255), nullable=False)
    file_type = Column(String(50), nullable=False)  # PDF, CSV
    file_size = Column(Integer, nullable=False)
    storage_path = Column(String(500), nullable=False)
    status = Column(String(50), default="processing", nullable=False)  # processing, completed, failed
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("Profile")
    extracted_tables = relationship("ExtractedTable", back_populates="document", cascade="all, delete-orphan")
    chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")
