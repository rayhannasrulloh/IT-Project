import uuid
from datetime import datetime
from sqlalchemy import Column, String, ForeignKey, DateTime, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base

class ExtractedTable(Base):
    __tablename__ = "extracted_tables"

    table_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    document_id = Column(String, ForeignKey("uploaded_documents.document_id"), nullable=False)
    table_name = Column(String(100), nullable=False)
    headers = Column(JSON, nullable=False)  # List of string headers
    rows = Column(JSON, nullable=False)  # List of lists/dicts representing row data
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    document = relationship("UploadedDocument", back_populates="extracted_tables")
