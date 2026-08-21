from datetime import datetime
from typing import Optional
from sqlalchemy import String, DateTime, Boolean, Index
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database import Base


class User(Base):
    """User account model with Authentication and Role-based Authorization."""
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    role: Mapped[str] = mapped_column(String(50), default="user", nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )


class EmailAccount(Base):
    """User's email account for receipt matching."""
    __tablename__ = "email_accounts"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(index=True)
    
    # Email provider settings
    imap_host: Mapped[str] = mapped_column(String(255))
    email_address: Mapped[str] = mapped_column(String(255))
    
    # Preferences
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
