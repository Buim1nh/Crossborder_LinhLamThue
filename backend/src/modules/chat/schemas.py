"""
MODULE 6 - Pydantic schemas & internal dataclasses for the chat pipeline.
"""
from datetime import datetime
from typing import Any, Literal, Optional

from pydantic import BaseModel, Field, field_validator



# ============================================================================
# API request / response
# ============================================================================

class ChatRequest(BaseModel):
    """Incoming chat message."""
    message: str = Field(..., min_length=1, max_length=2000)
    user_id: Optional[int] = Field(
        default=None,
        description="Owner of the financial data used to build context.",
    )

    @field_validator("message")
    @classmethod
    def _reject_blank(cls, v: str) -> str:
        """`min_length=1` still lets through whitespace-only input, which
        would waste an LLM call on an empty question."""
        stripped = v.strip()
        if not stripped:
            raise ValueError("message must not be empty or whitespace only")
        return stripped



class ChatResponse(BaseModel):
    """Outgoing chat answer. `disclaimer` is ALWAYS populated."""
    response: str
    blocked: bool = False
    block_reason: Optional[str] = None
    disclaimer: str
    model: Optional[str] = None
    context_used: Optional[dict[str, Any]] = None


# ============================================================================
# Safety filter
# ============================================================================

class SafetyVerdict(BaseModel):
    """Result of running the safety filter over a user message."""
    allowed: bool
    reason: Optional[str] = None
    matched_pattern: Optional[str] = None
    decline_message: Optional[str] = None


# ============================================================================
# Context (built from the database, fed to the prompt)
# ============================================================================

class TransactionBrief(BaseModel):
    """Compact transaction view used inside prompts."""
    date: str
    amount: float
    currency: str = "USD"
    description: str
    merchant: Optional[str] = None
    category: Optional[str] = None
    type: Optional[str] = None


class AnomalyBrief(BaseModel):
    """Compact anomaly view used inside prompts."""
    description: str
    level: Optional[str] = None
    reason: Optional[str] = None
    date: Optional[str] = None
    dispute_deadline: Optional[str] = None


class SubscriptionBrief(BaseModel):
    """Active recurring charge."""
    name: str
    amount: float
    currency: str = "USD"
    last_charge: Optional[str] = None
    next_charge: Optional[str] = None


class ReconciliationStatus(BaseModel):
    """How well statement rows match up with email receipts."""
    matched: int = 0
    no_email_found: int = 0
    suspicious: int = 0
    unchecked: int = 0

    @property
    def total(self) -> int:
        return self.matched + self.no_email_found + self.suspicious + self.unchecked


class FinancialSummary(BaseModel):
    """Aggregate money-in / money-out figures."""
    total_spending: float = 0.0
    total_income: float = 0.0
    total_fees: float = 0.0
    net_flow: float = 0.0
    currency: str = "USD"
    transaction_count: int = 0
    period_start: Optional[str] = None
    period_end: Optional[str] = None
    by_category: dict[str, float] = Field(default_factory=dict)


class UserContext(BaseModel):
    """Everything the LLM is allowed to know about the user's finances."""
    user_id: Optional[int] = None
    recent_transactions: list[TransactionBrief] = Field(default_factory=list)
    anomalies: list[AnomalyBrief] = Field(default_factory=list)
    subscriptions: list[SubscriptionBrief] = Field(default_factory=list)
    reconciliation_status: ReconciliationStatus = Field(
        default_factory=ReconciliationStatus
    )
    financial_summary: FinancialSummary = Field(default_factory=FinancialSummary)
    ml_anomaly_summary: Optional[dict[str, Any]] = Field(
        default=None,
        description="Summary from TransactionAnomalyDetector ML model including risk tiers"
    )
    ml_anomalies: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Detected anomalies from ML model with risk_tier, anomaly_score"
    )
    generated_at: datetime = Field(default_factory=datetime.utcnow)

    @property
    def is_empty(self) -> bool:
        """True when there is no financial data to reason about."""
        return self.financial_summary.transaction_count == 0


# ============================================================================
# LLM transport
# ============================================================================

LLMProviderName = Literal["anthropic", "openai", "gemini", "mock"]


class LLMResult(BaseModel):
    """Normalized response from any provider."""
    content: str
    model: str
    provider: str
    usage: Optional[dict[str, Any]] = None
