import uuid
from datetime import datetime
from sqlalchemy import Column, String, ForeignKey, DateTime, Text, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base

class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    chunk_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    document_id = Column(String, ForeignKey("uploaded_documents.document_id"), nullable=False)
    content = Column(Text, nullable=False)
    metadata_json = Column(JSON, nullable=True)
    embedding = Column(JSON, nullable=True)  # Fallback vector representation (JSON float list)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    document = relationship("UploadedDocument", back_populates="chunks")
