from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    # unique=True means no two users can share the same email.
    # nullable=False means this field is required — can't be empty.
    email = Column(String, unique=True, index=True, nullable=False)

    username = Column(String, unique=True, index=True, nullable=False)

    # NEVER store real passwords. Only the hashed version.
    hashed_password = Column(String, nullable=False)

    # is_active lets us "soft-disable" a user without deleting their data.
    is_active = Column(Boolean, default=True)

    # is_admin controls who can create/edit products.
    is_admin = Column(Boolean, default=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    orders = relationship("Order", back_populates="user")