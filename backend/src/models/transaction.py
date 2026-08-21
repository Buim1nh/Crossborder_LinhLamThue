import enum
from datetime import datetime
from typing import Optional
from sqlalchemy import String, Float, DateTime, Enum, Text, Integer
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database import Base


class TransactionType(str, enum.Enum):
    """Types of transactions."""
    PAYIN = "payin"              # Tiền nạp vào
    PAYOUT = "payout"            # Tiền rút/chuyển ra
    CARD_SPEND = "card_spend"    # Chi tiêu thẻ
    CARD_TRANSFER = "card_transfer"  # Chuyển từ tài khoản sang thẻ
    FEE = "fee"                  # Phí
    REFUND = "refund"            # Hoàn tiền


class AlertLevel(str, enum.Enum):
    """Alert levels for flagged transactions."""
    REGULAR = "regular"          # Định kỳ đã xác định
    NEEDS_CONFIRMATION = "needs_confirmation"  # Cần bạn tự xác nhận
    INSUFFICIENT_DATA = "insufficient_data"   # Chưa đủ dữ liệu


class Transaction(Base):
    """Transaction model."""
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(primary_key=True)

    # User ownership
    user_id: Mapped[int] = mapped_column(Integer, nullable=False)

    # Source identification
    source: Mapped[str] = mapped_column(String(20))  # "account" | "wallet" | "card"
    source_id: Mapped[str] = mapped_column(String(100))  # Original ID from source
    
    # Transaction details
    type: Mapped[TransactionType] = mapped_column(Enum(TransactionType))
    amount: Mapped[float] = mapped_column(Float)
    currency: Mapped[str] = mapped_column(String(3), default="USD")
    
    # Description & categorization
    description: Mapped[str] = mapped_column(Text)
    merchant_name: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    category: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    # Dates
    transaction_date: Mapped[datetime] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Email matching
    email_match_status: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)  
    # "matched" | "no_email_found" | "suspicious" | null
    
    # Alert & flags
    is_flagged: Mapped[bool] = mapped_column(default=False)
    alert_level: Mapped[Optional[AlertLevel]] = mapped_column(Enum(AlertLevel), nullable=True)
    alert_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Subscription detection
    is_subscription: Mapped[bool] = mapped_column(default=False)
    subscription_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    next_charge_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Dispute deadline (60 days from statement date)
    dispute_deadline: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Masked card number (last 4 digits only)
    masked_card: Mapped[Optional[str]] = mapped_column(String(4), nullable=True)
