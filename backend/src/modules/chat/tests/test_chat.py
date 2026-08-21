"""
MODULE 6 test suite.

Covers the two guarantees the module must never break:
  1. Unsafe requests are blocked BEFORE any DB/LLM access.
  2. Every response carries the mandatory disclaimer.

Plus prompt/context rendering and the pipeline wiring.
"""
import pytest

from src.modules.chat.config import DISCLAIMER
from src.modules.chat.prompt_builder import (
    SYSTEM_PROMPT,
    build_context_block,
    build_prompt,
)
from src.modules.chat.safety_filter import check_message, is_blocked, normalize
from src.modules.chat.schemas import (
    AnomalyBrief,
    ChatRequest,
    FinancialSummary,
    SubscriptionBrief,
    TransactionBrief,
    UserContext,
)

from src.modules.chat.service import ERROR_FALLBACK, ensure_disclaimer, handle_chat


# ============================================================================
# Safety filter — blocked patterns from the spec
# ============================================================================

@pytest.mark.parametrize(
    "message,expected_reason",
    [
        ("huỷ gói", "action_cancel"),
        ("hủy gói Netflix giúp mình", "action_cancel"),
        ("huy goi spotify", "action_cancel"),
        ("Bạn huỷ dịch vụ này cho tôi nhé", "action_cancel"),
        ("cancel subscription này giúp mình", "action_cancel"),
        ("khiếu nại cho shop ABC", "action_complaint"),
        ("khieu nai cho shop XYZ giup toi", "action_complaint"),
        ("giúp tôi chargeback giao dịch này", "action_complaint"),
        ("tài khoản này có an toàn không", "assurance_safety"),
        ("tài khoản an toàn không?", "assurance_safety"),
        ("tai khoan nay co an toan khong", "assurance_safety"),
        ("chuyển tiền giúp mình 500k", "action_money_move"),
    ],
)
def test_blocked_messages(message, expected_reason):
    """Spec-listed unsafe requests must be declined with the right reason."""
    verdict = check_message(message)
    assert verdict.allowed is False, f"should be blocked: {message}"
    assert verdict.reason == expected_reason
    assert verdict.decline_message


@pytest.mark.parametrize(
    "message",
    [
        "chi bao nhiêu",
        "Tháng này tôi chi bao nhiêu tiền?",
        "khoản này là gì",
        "Khoản 250k ngày 12/03 là gì vậy?",
        "gói định kỳ nào",
        "Gói định kỳ nào đang chạy trên tài khoản?",
        "Có giao dịch nào bất thường không?",
        "Tôi đã trả bao nhiêu phí trong kỳ này?",
    ],
)
def test_safe_messages_pass(message):
    """Ordinary analytical questions must never be blocked."""
    verdict = check_message(message)
    assert verdict.allowed is True, f"should pass: {message} ({verdict.reason})"


# ---------------------------------------------------------------------------
# Under-blocking regressions: phrasings that slipped past the first blocklist
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "message,expected_reason",
    [
        # "tài khoản" and "an toàn" separated by an arbitrary clause.
        ("tài khoản của tôi có an toàn không", "assurance_safety"),
        ("tài khoản này an toàn chứ", "assurance_safety"),
        ("tôi có bị lừa đảo không", "assurance_safety"),
        # Delegation verbs beyond "chuyển tiền".
        ("thanh toán hộ mình", "action_money_move"),
        ("rút tiền dùm mình", "action_money_move"),
        ("đòi lại tiền giúp mình", "action_complaint"),
        ("báo cáo shop này", "action_complaint"),
        ("huỷ thuê bao", "action_cancel"),
    ],
)
def test_delegation_variants_are_blocked(message, expected_reason):
    """Paraphrases of a delegation request must not slip through."""
    verdict = check_message(message)
    assert verdict.allowed is False, f"should be blocked: {message}"
    assert verdict.reason == expected_reason


# ---------------------------------------------------------------------------
# Over-blocking regressions: how-to questions the system prompt invites
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "message",
    [
        "làm sao để huỷ gói Netflix",
        "cách huỷ gói Spotify là gì",
        "tôi nên khiếu nại ở đâu",
        "quy trình khiếu nại như thế nào",
        "hạn khiếu nại của giao dịch này là bao lâu",
    ],
)
def test_guidance_questions_are_allowed(message):
    """
    Asking HOW to cancel/dispute is in scope — the assistant explains the
    steps, the user performs them. Only "do it for me" is refused.
    """
    verdict = check_message(message)
    assert verdict.allowed is True, f"should pass: {message} ({verdict.reason})"


@pytest.mark.parametrize(
    "message,expected_reason",
    [
        # A delegation phrase overrides guidance wording.
        ("làm sao huỷ gói giúp mình", "action_cancel"),
        ("hướng dẫn khiếu nại thay tôi", "action_complaint"),
        # Guidance never rescues safety assurance or moving money.
        ("làm sao biết tài khoản của tôi có an toàn không", "assurance_safety"),
        ("hướng dẫn chuyển tiền giúp mình", "action_money_move"),
    ],
)
def test_guidance_does_not_rescue_delegation(message, expected_reason):
    """The allowlist must not become a bypass for the blocklist."""
    verdict = check_message(message)
    assert verdict.allowed is False, f"should be blocked: {message}"
    assert verdict.reason == expected_reason


def test_normalize_strips_diacritics():
    assert normalize("Huỷ Gói  Netflix") == "huy goi netflix"

    assert normalize("Đặt lịch") == "dat lich"
    assert normalize("") == ""


def test_is_blocked_helper():
    assert is_blocked("huỷ gói giúp mình") is True
    assert is_blocked("chi bao nhiêu tháng này") is False


# ============================================================================
# Disclaimer enforcement
# ============================================================================

def test_disclaimer_appended_when_missing():
    result = ensure_disclaimer("Tháng này bạn chi 1.000.000 VND.")
    assert DISCLAIMER in result


def test_disclaimer_not_duplicated():
    text = f"Bạn chi 1.000.000 VND.\n\n{DISCLAIMER}"
    result = ensure_disclaimer(text)
    assert result.count("chỉ hỗ trợ bạn rà soát tài chính") == 1


def test_system_prompt_embeds_disclaimer():
    assert DISCLAIMER in SYSTEM_PROMPT


# ============================================================================
# Request validation
# ============================================================================

@pytest.mark.parametrize("blank", ["   ", "\n\t", "  \n  "])
def test_blank_message_rejected(blank):
    """Whitespace-only input must not reach the pipeline (min_length=1 alone
    would let it through)."""
    with pytest.raises(ValueError):
        ChatRequest(message=blank)


def test_message_is_stripped():
    assert ChatRequest(message="  chi bao nhiêu?  ").message == "chi bao nhiêu?"



# ============================================================================
# Context / prompt rendering
# ============================================================================

def _sample_context() -> UserContext:
    return UserContext(
        user_id=1,
        recent_transactions=[
            TransactionBrief(
                date="2026-03-12",
                amount=250000,
                currency="VND",
                description="NETFLIX.COM",
                merchant="Netflix",
                category="Entertainment",
                type="card_spend",
            )
        ],
        anomalies=[
            AnomalyBrief(
                description="Netflix - 250000 VND",
                level="warning",
                reason="Charged twice in one day",
                date="2026-03-12",
                dispute_deadline="2026-04-11",
            )
        ],
        subscriptions=[
            SubscriptionBrief(
                name="Netflix",
                amount=250000,
                currency="VND",
                last_charge="2026-03-12",
                next_charge="2026-04-12",
            )
        ],
        financial_summary=FinancialSummary(
            total_spending=1000000,
            total_income=3000000,
            total_fees=15000,
            net_flow=1985000,
            currency="VND",
            transaction_count=12,
            by_category={"Entertainment": 250000},
        ),
    )


def test_context_block_includes_all_sections():
    block = build_context_block(_sample_context())
    assert "Tổng chi" in block
    assert "Netflix" in block
    assert "hạn khiếu nại: 2026-04-11" in block
    assert "Gói định kỳ đang hoạt động" in block
    assert "Đối soát với email hoá đơn" in block


def test_empty_context_is_explicit():
    block = build_context_block(UserContext())
    assert "Chưa có giao dịch nào" in block


def test_build_prompt_contains_question():
    _, user_prompt = build_prompt("Chi bao nhiêu?", _sample_context())
    assert "Chi bao nhiêu?" in user_prompt
    assert "DỮ LIỆU NGƯỜI DÙNG" in user_prompt


# ============================================================================
# Pipeline
# ============================================================================

class _FakeDB:
    """Stand-in for AsyncSession; fails loudly if the pipeline queries it."""

    def __init__(self):
        self.queried = False

    async def execute(self, *_args, **_kwargs):
        self.queried = True
        raise AssertionError("DB should not be queried for blocked messages")


@pytest.mark.asyncio
async def test_blocked_message_skips_database_and_llm():
    """Safety filter short-circuits before context building."""
    db = _FakeDB()
    response = await handle_chat("huỷ gói Netflix giúp mình", db)

    assert response.blocked is True
    assert response.block_reason == "action_cancel"
    assert db.queried is False
    assert DISCLAIMER in response.response
    assert response.context_used is None


@pytest.mark.asyncio
async def test_allowed_message_runs_full_pipeline(monkeypatch):
    """A safe question reaches the LLM and comes back with a disclaimer."""
    from src.modules.chat import service

    async def fake_context(_db, user_id=None):
        return _sample_context()

    monkeypatch.setattr(service, "build_user_context", fake_context)

    response = await handle_chat("Tháng này tôi chi bao nhiêu?", db=None)

    assert response.blocked is False
    assert DISCLAIMER in response.response
    assert response.context_used["transaction_count"] == 12
    assert response.context_used["anomalies"] == 1


@pytest.mark.asyncio
async def test_llm_failure_returns_safe_fallback(monkeypatch):
    """Provider errors surface as a friendly message, never a stack trace."""
    from src.modules.chat import service

    async def fake_context(_db, user_id=None):
        return _sample_context()

    class BrokenProvider:
        async def complete(self, *_args, **_kwargs):
            raise RuntimeError("upstream 500")

    monkeypatch.setattr(service, "build_user_context", fake_context)
    monkeypatch.setattr(service, "get_provider", lambda: BrokenProvider())

    response = await handle_chat("Chi bao nhiêu?", db=None)

    assert ERROR_FALLBACK in response.response
    assert DISCLAIMER in response.response
    assert response.blocked is False
