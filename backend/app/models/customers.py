from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime
from sqlalchemy.orm import relationship
from app.core.database import Base

class Customer(Base):
    __tablename__ = "customers"

    customer_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    city = Column(String(100), nullable=False)
    tier = Column(String(20), nullable=False)  # Premium, Standard, Basic
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    orders = relationship("Order", back_populates="customer")
