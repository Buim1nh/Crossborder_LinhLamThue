"""
MODULE 6 - Step 1: SAFETY FILTER.

The first gate in the chat pipeline. It runs BEFORE any database access or
LLM call, so blocked requests never cost a token and never touch user data.

Design notes
------------
Vietnamese users type with inconsistent diacritics ("huỷ" vs "hủy" vs "huy").
Rather than enumerate every spelling, we normalize the message to a
diacritics-free lowercase form and match regexes against that.

The filter is intentionally conservative in scope: it blocks requests asking
the assistant to ACT on the user's behalf (cancel, dispute, move money) or to
give a SAFETY GUARANTEE. Ordinary analytical questions must always pass.
"""
import re
import unicodedata
from typing import Optional

from src.modules.chat.config import BLOCKED_PATTERNS, DECLINE_MESSAGES
from src.modules.chat.schemas import SafetyVerdict


def normalize(text: str) -> str:
    """
    Lowercase, strip Vietnamese diacritics, and collapse whitespace.

    "Huỷ gói Netflix giúp mình!" -> "huy goi netflix giup minh!"

    Uses NFD decomposition to split base characters from their combining
    accents, then drops the accents. `đ`/`Đ` has no combining form so it is
    replaced explicitly.
    """
    if not text:
        return ""

    lowered = text.lower().replace("đ", "d")
    decomposed = unicodedata.normalize("NFD", lowered)
    stripped = "".join(
        ch for ch in decomposed if unicodedata.category(ch) != "Mn"
    )
    # Re-compose and squeeze runs of whitespace to single spaces so that
    # patterns using \s+ behave predictably.
    return re.sub(r"\s+", " ", unicodedata.normalize("NFC", stripped)).strip()


# Pre-compile once at import time.
_COMPILED_PATTERNS: list[tuple[re.Pattern, str, str]] = [
    (re.compile(pattern), reason, pattern)
    for pattern, reason in BLOCKED_PATTERNS
]


def check_message(message: str) -> SafetyVerdict:
    """
    Run the safety filter over a user message.

    Returns a SafetyVerdict. When `allowed` is False, `decline_message`
    holds a polite, actionable refusal that redirects the user toward
    something the assistant CAN legitimately do.
    """
    normalized = normalize(message)

    for compiled, reason, raw_pattern in _COMPILED_PATTERNS:
        if compiled.search(normalized):
            return SafetyVerdict(
                allowed=False,
                reason=reason,
                matched_pattern=raw_pattern,
                decline_message=get_decline_message(reason),
            )

    return SafetyVerdict(allowed=True)


def get_decline_message(reason: Optional[str]) -> str:
    """Look up the polite decline text for a reason code."""
    if reason and reason in DECLINE_MESSAGES:
        return DECLINE_MESSAGES[reason]
    return DECLINE_MESSAGES["default"]


def is_blocked(message: str) -> bool:
    """Convenience boolean check, useful in tests and guards."""
    return not check_message(message).allowed
