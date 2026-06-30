from sqlalchemy import Column, String, Integer, Numeric
from sqlalchemy.orm import relationship
from app.core.database import Base

class Product(Base):
    __tablename__ = "products"

    product_id = Column(Integer, primary_key=True, autoincrement=True)
    product_name = Column(String(150), nullable=False)
    category = Column(String(100), nullable=False)
    unit_price = Column(Numeric(10, 2), nullable=False)
    cost = Column(Numeric(10, 2), nullable=False)

    order_items = relationship("OrderItem", back_populates="product")
