"""
MODULE 7 - ML inference configuration.

Every tunable knob for the inference pipeline lives here so the module stays
self-contained and can be dropped into another project by copying one folder.

Design note: the module NEVER hard-requires scikit-learn. When an artifact or
the library is missing, each predictor falls back to a deterministic heuristic
(see `predictors/`). That mirrors the chat module's `MockProvider` approach and
keeps a fresh checkout runnable with zero setup.
"""
from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings

# Repo-relative default: backend/src/modules/ml/artifacts
_MODULE_DIR = Path(__file__).resolve().parent
_DEFAULT_ARTIFACT_DIR = _MODULE_DIR / "artifacts"


# ============================================================================
# CATEGORY TAXONOMY
# ============================================================================
# Kept flat and small on purpose: a shallow taxonomy is far easier for a model
# (and a human) to be consistent about than a deep one.
CATEGORIES: tuple[str, ...] = (
    "subscription",
    "food_drink",
    "shopping",
    "transport",
    "utilities",
    "health",
    "entertainment",
    "transfer",
    "fee",
    "income",
    "other",
)

UNKNOWN_CATEGORY = "other"


# ============================================================================
# HEURISTIC FALLBACK KEYWORDS
# ============================================================================
# Used when no trained categorizer artifact is available. Order matters only in
# that the highest keyword-hit count wins; ties break toward the earlier entry.
CATEGORY_KEYWORDS: dict[str, tuple[str, ...]] = {
    "subscription": (
        "netflix", "spotify", "hulu", "disney", "hbo", "youtube premium",
        "apple music", "adobe", "dropbox", "google one", "icloud",
        "membership", "subscription", "premium", "prime",
    ),
    "food_drink": (
        # Vietnamese terms are matched post-diacritic-stripping, so they are
        # listed here unaccented ("cà phê" -> "ca phe").
        "ca phe", "quan an", "nha hang", "com tam", "banh mi", "tra sua",
        "restaurant", "cafe", "coffee", "starbucks", "highlands", "grabfood",
        "shopeefood", "baemin", "pizza", "burger", "bakery", "food", "dining",
    ),
    "shopping": (
        "amazon", "shopee", "lazada", "tiki", "ebay", "aliexpress", "store",
        "shop", "mall", "uniqlo", "zara", "market",
    ),
    "transport": (
        "grab", "uber", "taxi", "gojek", "be group", "fuel", "petrol",
        "gas station", "parking", "airline", "vietjet", "bamboo", "railway",
    ),
    "utilities": (
        "electric", "water bill", "internet", "telecom", "viettel", "vinaphone",
        "mobifone", "fpt", "utility", "gas bill", "rent",
    ),
    "health": (
        "pharmacy", "clinic", "hospital", "medical", "dental", "insurance",
        "guardian", "long chau", "pharmacity",
    ),
    "entertainment": (
        "cinema", "cgv", "lotte cinema", "steam", "playstation", "xbox",
        "game", "concert", "ticket",
    ),
    "transfer": (
        "transfer", "chuyen khoan", "ck ", "remittance", "wise", "paypal",
        "payout", "withdraw",
    ),
    "fee": (
        "fee", "charge", "phi ", "commission", "interest", "surcharge", "tax",
    ),
    "income": (
        "salary", "payroll", "luong", "refund", "cashback", "bonus",
        "deposit", "payin",
    ),
}


# ============================================================================
# ANOMALY SCORING
# ============================================================================
# Weights for the heuristic anomaly scorer. They sum to 1.0 so the resulting
# score is directly interpretable as a 0..1 risk value.
ANOMALY_SIGNAL_WEIGHTS: dict[str, float] = {
    "amount_outlier": 0.40,   # unusually large vs. the user's own history
    "rare_merchant": 0.20,    # merchant seen once or never before
    "odd_hour": 0.15,         # transacted between 00:00-05:00
    "round_amount": 0.10,     # suspiciously round figure (e.g. exactly 500.00)
    "rapid_repeat": 0.15,     # same merchant+amount within a short window
}

# A robust z-score (median/MAD based) above this is treated as a full outlier.
AMOUNT_ZSCORE_CAP = 6.0

# Two identical charges closer than this are considered a "rapid repeat".
RAPID_REPEAT_WINDOW_SECONDS = 24 * 3600

# Below this many historical transactions the statistics are not trustworthy,
# so the scorer reports `insufficient_data` instead of inventing a number.
MIN_HISTORY_FOR_STATS = 5


class MLSettings(BaseSettings):
    """
    Module-local settings.

    Reads the same `.env` as the host app. All keys are prefixed `ML_` so they
    cannot collide with the app-wide or chat-module settings.
    """

    # Master switch. When False, the service short-circuits and reports that
    # inference is disabled rather than silently returning heuristic output.
    ML_ENABLED: bool = True

    # Where trained artifacts live. Override in production to point at a
    # mounted volume or a path populated by your deployment pipeline.
    ML_ARTIFACT_DIR: str = str(_DEFAULT_ARTIFACT_DIR)

    # Artifact filenames inside ML_ARTIFACT_DIR.
    ML_CATEGORIZER_ARTIFACT: str = "categorizer.joblib"
    ML_ANOMALY_ARTIFACT: str = "anomaly_scorer.joblib"

    # Path to TransactionAnomalyDetector checkpoint (trained model)
    # Default: repo-relative path to ../../../../checkpoints/archive/TransactionAnomalyDetector
    ML_TRANSACTION_ANOMALY_PATH: str = str(
        Path(__file__).resolve().parents[4] / "checkpoints" / "archive" / "TransactionAnomalyDetector"
    )

    # Predictions below this confidence are downgraded to UNKNOWN_CATEGORY
    # rather than surfacing a guess the UI would present as fact.
    ML_MIN_CONFIDENCE: float = 0.35

    # Score at/above which a transaction is flagged for user confirmation.
    ML_ANOMALY_THRESHOLD: float = 0.65

    # Guardrail so a single request cannot pin the event loop.
    ML_MAX_BATCH_SIZE: int = 500

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"

    @property
    def artifact_dir(self) -> Path:
        return Path(self.ML_ARTIFACT_DIR)

    @property
    def categorizer_path(self) -> Path:
        return self.artifact_dir / self.ML_CATEGORIZER_ARTIFACT

    @property
    def anomaly_path(self) -> Path:
        return self.artifact_dir / self.ML_ANOMALY_ARTIFACT


@lru_cache()
def get_ml_settings() -> MLSettings:
    return MLSettings()
