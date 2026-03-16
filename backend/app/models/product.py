from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String, nullable=False, index=True)

    description = Column(Text)

    price = Column(Float, nullable=False)

    stock = Column(Integer, default=0)

    # Category for filtering — "shoes", "shirts", "accessories", etc.
    category = Column(String, index=True)

    # A URL pointing to a product image — we store the link, not the image itself.
    image_url = Column(String)

    # is_available lets us hide a product without deleting it.
    is_available = Column(Boolean, default=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # updated_at automatically updates whenever this row is changed.
    # onupdate=func.now() is the hook that does that.
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    order_items = relationship("OrderItem", back_populates="product")