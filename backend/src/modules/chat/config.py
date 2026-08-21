"""
MODULE 6 - Chat module configuration.

All tunable knobs for the chat pipeline live here so the module stays
self-contained and can be dropped into another project by copying one folder.
"""
from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings


# ============================================================================
# MANDATORY DISCLAIMER
# Per spec: must be present in EVERY response returned by this module.
# ============================================================================
DISCLAIMER = (
    "⚠️ Công cụ này chỉ hỗ trợ bạn rà soát tài chính, không thay thế tư vấn "
    "tài chính/pháp lý và không thực hiện bất kỳ giao dịch nào thay bạn. "
    "Mọi quyết định cuối cùng thuộc về bạn."
)

# A short signature used to detect whether the disclaimer is already present
# in the LLM output (models often paraphrase, so we match on a stable prefix).
DISCLAIMER_FINGERPRINT = "chỉ hỗ trợ bạn rà soát tài chính"


# ============================================================================
# SAFETY FILTER PATTERNS
# ============================================================================
# Requests that imply the assistant would ACT on behalf of the user
# (cancel a plan, file a complaint) or give a guarantee/assurance
# ("is my account safe?") must be declined.
#
# Patterns are matched against a diacritics-stripped, lowercased form of the
# message, so "huỷ gói" / "hủy gói" / "huy goi" all match the same rule.
BLOCKED_PATTERNS: list[tuple[str, str]] = [
    # (regex against normalized text, reason code)
    (r"\bhuy\s+(goi|dich\s*vu|dang\s*ky|subscription|thue\s*bao)\b", "action_cancel"),
    (r"\b(cancel|unsubscribe)\b", "action_cancel"),
    (r"\bhuy\s+(giup|ho|dum)\b", "action_cancel"),
    (r"\bkhieu\s*nai\b", "action_complaint"),
    (r"\b(chargeback|doi\s+tien|doi\s+lai\s+tien)\b", "action_complaint"),
    (r"\bbao\s*cao\s+(shop|nguoi\s*ban|merchant)\b", "action_complaint"),
    (r"\btai\s*khoan\s+(nay\s+)?(co\s+)?an\s*toan\b", "assurance_safety"),
    (r"\bco\s+bi\s+(hack|lua|scam|lua\s*dao)\s+khong\b", "assurance_safety"),
    (r"\b(chuyen|thanh\s*toan|rut)\s+tien\s+(giup|ho|dum)\b", "action_money_move"),
]

# Polite decline messages keyed by reason code.
DECLINE_MESSAGES: dict[str, str] = {
    "action_cancel": (
        "Mình rất tiếc, mình không thể huỷ gói dịch vụ hay đăng ký thay bạn. "
        "Mình chỉ có thể giúp bạn *nhận diện* các khoản định kỳ đang bị trừ tiền "
        "và cho biết khoản đó đến từ đâu, để bạn tự thao tác huỷ trên trang của "
        "nhà cung cấp nhé.\n\n"
        "Bạn có muốn mình liệt kê các gói định kỳ đang hoạt động không?"
    ),
    "action_complaint": (
        "Mình không thể gửi khiếu nại hay yêu cầu hoàn tiền thay bạn. "
        "Việc này cần chính bạn thực hiện với ngân hàng/đơn vị phát hành thẻ.\n\n"
        "Điều mình có thể làm: tổng hợp lại chi tiết giao dịch (ngày, số tiền, "
        "mô tả, hạn khiếu nại còn lại) để bạn có đủ thông tin khi làm việc với họ. "
        "Bạn có muốn mình tổng hợp không?"
    ),
    "assurance_safety": (
        "Mình không thể khẳng định tài khoản của bạn có an toàn hay không — "
        "mình không có quyền truy cập hệ thống bảo mật của ngân hàng và không "
        "được phép đưa ra bảo đảm như vậy.\n\n"
        "Nếu bạn nghi ngờ có vấn đề, hãy liên hệ trực tiếp ngân hàng/đơn vị phát "
        "hành thẻ ngay. Mình có thể giúp bạn rà soát xem có giao dịch nào bất "
        "thường trong dữ liệu sao kê để bạn đối chiếu."
    ),
    "action_money_move": (
        "Mình không thể thực hiện chuyển tiền, thanh toán hay rút tiền thay bạn. "
        "Mình chỉ đọc và phân tích dữ liệu sao kê bạn đã tải lên.\n\n"
        "Mình có thể giúp bạn rà soát các khoản chi gần đây nếu bạn muốn."
    ),
    "default": (
        "Mình xin phép không hỗ trợ yêu cầu này. Mình chỉ có thể giúp bạn rà "
        "soát và giải thích dữ liệu tài chính của chính bạn, không thay bạn "
        "thực hiện thao tác nào."
    ),
}


# ============================================================================
# PROMPT / CONTEXT LIMITS
# ============================================================================
RECENT_TRANSACTIONS_LIMIT = 5
ANOMALIES_LIMIT = 5
SUBSCRIPTIONS_LIMIT = 10
MAX_MESSAGE_LENGTH = 2000


class ChatSettings(BaseSettings):
    """
    Module-local settings.

    Reads the same `.env` as the host app. Falls back to the app-wide
    LLM_* variables so the module works with zero extra configuration,
    but can be overridden with CHAT_* variables when you want the chat
    module to use a different model than the rest of the system.
    """

    # Provider: anthropic | openai | gemini | mock
    CHAT_LLM_PROVIDER: Optional[str] = None
    CHAT_LLM_API_KEY: Optional[str] = None
    CHAT_LLM_MODEL: Optional[str] = None

    # Inherited app-level defaults
    LLM_PROVIDER: str = "anthropic"
    LLM_API_KEY: str = ""
    LLM_MODEL: str = "claude-3-sonnet-20240229"

    # Generation params
    CHAT_MAX_TOKENS: int = 1024
    CHAT_TEMPERATURE: float = 0.3
    CHAT_TIMEOUT_SECONDS: float = 30.0

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"

    @property
    def provider(self) -> str:
        return (self.CHAT_LLM_PROVIDER or self.LLM_PROVIDER or "mock").lower()

    @property
    def api_key(self) -> str:
        return self.CHAT_LLM_API_KEY or self.LLM_API_KEY or ""

    @property
    def model(self) -> str:
        return self.CHAT_LLM_MODEL or self.LLM_MODEL


@lru_cache()
def get_chat_settings() -> ChatSettings:
    return ChatSettings()
