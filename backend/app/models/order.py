from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.database import Base


# Python enums make allowed values explicit and typo-proof.
class OrderStatus(str, enum.Enum):
    pending   = "pending"
    confirmed = "confirmed"
    shipped   = "shipped"
    delivered = "delivered"
    cancelled = "cancelled"


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)

    # ForeignKey means this column points to a row in another table.
    # "users.id" means: the id column of the users table.
    # This is to know which user placed this order.
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Important: prices can change later, so we snapshot the total here.
    total_price = Column(Float, nullable=False)

    # Enum column — only the values defined in OrderStatus are allowed.
    # default="pending" means all new orders start in the pending state.
    status = Column(
        Enum(OrderStatus),
        default=OrderStatus.pending,
        nullable=False
    )

    shipping_address = Column(String)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships — back_populates wires them together bidirectionally.
    # So order.user gives the User object, and user.orders gives a list of Orders.
    user  = relationship("User", back_populates="orders")

    # One order contains many line items (each product is one item).
    items = relationship("OrderItem", back_populates="order")


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)

    order_id   = Column(Integer, ForeignKey("orders.id"),   nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)

    # How many units of this product were ordered.
    quantity = Column(Integer, nullable=False, default=1)

    # Price at time of purchase — snapshot again.
    # If a product's price changes tomorrow, past orders stay correct.
    unit_price = Column(Float, nullable=False)

    order   = relationship("Order",   back_populates="items")
    product = relationship("Product", back_populates="order_items")