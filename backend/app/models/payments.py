from datetime import datetime
from sqlalchemy import Column, Integer, ForeignKey, DateTime, String, Numeric
from sqlalchemy.orm import relationship
from app.core.database import Base

class Payment(Base):
    __tablename__ = "payments"

    payment_id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey("orders.order_id"), nullable=False)
    amount = Column(Numeric(12, 2), nullable=False)
    method = Column(String(50), nullable=False)  # Credit Card, PayPal, Bank Transfer
    paid_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    status = Column(String(50), nullable=False)  # Success, Failed, Pending

    order = relationship("Order", back_populates="payments")
