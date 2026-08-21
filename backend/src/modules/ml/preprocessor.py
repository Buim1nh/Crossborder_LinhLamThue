"""
MODULE 7 - Step 1: FEATURE ENGINEERING.

Turns a raw `TransactionInput` into a `FeatureVector`.

This is the single most important file to keep stable: if training and serving
build features differently, the model silently degrades ("training/serving
skew"). Any change here must be mirrored in the training script under
`training/` and the artifact version bumped.
"""
import math
import re
import unicodedata

from src.modules.ml.schemas import FeatureVector, TransactionInput

# Hours considered "odd" for consumer spending. Cards used at 3am are a classic
# fraud tell, though on its own it is weak evidence - hence a modest weight.
ODD_HOUR_START = 0
ODD_HOUR_END = 5

_NON_ALNUM = re.compile(r"[^a-z0-9\s]+")
_MULTI_SPACE = re.compile(r"\s+")

# Statement rows are full of noise that carries no categorical signal. Removing
# it makes the bag-of-words far denser and the keyword matcher more reliable.
_NOISE_TOKENS = frozenset({
    "pos", "atm", "pmt", "payment", "purchase", "debit", "credit", "card",
    "trans", "transaction", "ref", "id", "no", "vnd", "usd", "tid", "auth",
})


def normalize_text(value: str) -> str:
    """
    Lowercase, strip Vietnamese diacritics and punctuation, drop noise tokens.

    Diacritics are stripped so "Cà Phê" and "ca phe" collapse to one token,
    matching the approach already used by the chat module's safety filter.
    """
    if not value:
        return ""

    decomposed = unicodedata.normalize("NFD", value.lower())
    without_marks = "".join(
        ch for ch in decomposed if unicodedata.category(ch) != "Mn"
    )
    # Vietnamese "đ" has no combining form, so handle it explicitly.
    without_marks = without_marks.replace("đ", "d")

    cleaned = _NON_ALNUM.sub(" ", without_marks)
    cleaned = _MULTI_SPACE.sub(" ", cleaned).strip()

    tokens = [
        t for t in cleaned.split(" ")
        if t and t not in _NOISE_TOKENS and not t.isdigit()
    ]
    return " ".join(tokens)


def is_round_amount(amount: float) -> bool:
    """
    True for suspiciously round figures (100.00, 500.00, 1000.00).

    Legitimate retail spend rarely lands on an exact multiple of 100; card
    testing and manual fraudulent transfers frequently do.
    """
    abs_amount = abs(amount)
    if abs_amount < 100:
        return False
    return math.isclose(abs_amount % 100, 0.0, abs_tol=1e-9)


def build_features(transaction: TransactionInput) -> FeatureVector:
    """Build the feature vector for a single transaction."""
    amount = float(transaction.amount)
    abs_amount = abs(amount)

    merchant = (transaction.merchant_name or "").strip()
    text = normalize_text(f"{merchant} {transaction.description}".strip())

    # Date fields are optional on input; fall back to neutral values rather
    # than guessing "now", which would make results non-deterministic.
    hour = day_of_week = 0
    day_of_month = 1
    is_weekend = is_odd_hour = False

    if transaction.transaction_date is not None:
        dt = transaction.transaction_date
        hour = dt.hour
        day_of_week = dt.weekday()
        day_of_month = dt.day
        is_weekend = day_of_week >= 5
        is_odd_hour = ODD_HOUR_START <= hour <= ODD_HOUR_END

    tokens = text.split() if text else []

    return FeatureVector(
        amount=amount,
        abs_amount=abs_amount,
        # log1p keeps the scale sane and handles a 0.00 amount without blowing up.
        log_amount=math.log1p(abs_amount),
        is_round_amount=is_round_amount(amount),
        is_credit=amount > 0,
        hour=hour,
        day_of_week=day_of_week,
        day_of_month=day_of_month,
        is_weekend=is_weekend,
        is_odd_hour=is_odd_hour,
        text=text,
        text_length=len(text),
        token_count=len(tokens),
        has_merchant=bool(merchant),
    )


def build_features_batch(
    transactions: list[TransactionInput],
) -> list[FeatureVector]:
    """Vectorize a batch, preserving input order."""
    return [build_features(t) for t in transactions]


def merchant_key(transaction: TransactionInput) -> str:
    """
    Stable identity for a merchant, used for frequency statistics.

    Falls back to the normalized description when the parser could not isolate
    a merchant name, so grouping still works on messy statement rows.
    """
    merchant = (transaction.merchant_name or "").strip()
    if merchant:
        return normalize_text(merchant)
    return normalize_text(transaction.description)
