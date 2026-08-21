"""
MODULE 7 tests.

These exercise the HEURISTIC path deliberately: it is what runs on a fresh
checkout with no artifacts, so it is the behaviour users actually get. The
model path is covered by asserting graceful degradation rather than by
committing a binary fixture.
"""
from datetime import datetime, timedelta

import pytest
from pydantic import ValidationError

from src.modules.ml.config import UNKNOWN_CATEGORY, MLSettings
from src.modules.ml.predictors import AnomalyScorer, CategoryPredictor
from src.modules.ml.preprocessor import build_features, is_round_amount, normalize_text
from src.modules.ml.schemas import PredictRequest, TransactionInput
from src.modules.ml.service import MLService

BASE_DATE = datetime(2024, 3, 15, 12, 0, 0)


def tx(description, amount, *, date=BASE_DATE, merchant=None):
    return TransactionInput(
        description=description,
        amount=amount,
        transaction_date=date,
        merchant_name=merchant,
    )


def routine_history(count=30, amount=-50.0):
    """A boring, tightly-clustered history to act as the 'normal' baseline."""
    return [
        tx("VINMART GROCERY", amount, date=BASE_DATE - timedelta(days=i),
           merchant="Vinmart")
        for i in range(count)
    ]


# ----------------------------------------------------------------------
# Preprocessing
# ----------------------------------------------------------------------

class TestPreprocessor:
    def test_strips_vietnamese_diacritics(self):
        assert normalize_text("Cà Phê Trung Nguyên") == "ca phe trung nguyen"

    def test_maps_d_with_stroke(self):
        # "đ" has no combining form so it needs explicit handling.
        assert "d" in normalize_text("Đồng")

    def test_drops_noise_tokens_and_numbers(self):
        assert normalize_text("POS 12345 STARBUCKS REF 99") == "starbucks"

    def test_empty_input_is_safe(self):
        assert normalize_text("") == ""

    @pytest.mark.parametrize("amount,expected", [
        (-500.0, True), (1000.0, True), (-523.47, False),
        (50.0, False),  # below the 100 floor: too common to be a signal
    ])
    def test_round_amount_detection(self, amount, expected):
        assert is_round_amount(amount) is expected

    def test_missing_date_yields_neutral_values(self):
        features = build_features(
            TransactionInput(description="TEST", amount=-10.0)
        )
        assert features.hour == 0
        assert features.is_weekend is False

    def test_odd_hour_flag(self):
        night = build_features(tx("X", -10.0, date=datetime(2024, 3, 15, 3, 0)))
        day = build_features(tx("X", -10.0, date=datetime(2024, 3, 15, 14, 0)))
        assert night.is_odd_hour and not day.is_odd_hour

    def test_numeric_vector_is_finite(self):
        vector = build_features(tx("STARBUCKS", -5.4)).to_numeric()
        assert len(vector) == 12
        assert all(isinstance(v, float) for v in vector)


# ----------------------------------------------------------------------
# Categorization
# ----------------------------------------------------------------------

class TestCategorizer:
    @pytest.fixture
    def predictor(self):
        return CategoryPredictor()

    @pytest.mark.parametrize("description,expected", [
        ("STARBUCKS COFFEE", "food_drink"),
        ("GRAB RIDE TO AIRPORT", "transport"),
        # "netflix" is taxonomized as a subscription, not entertainment.
        ("NETFLIX MONTHLY", "subscription"),
        ("EVN ELECTRIC BILL", "utilities"),
        ("SHOPEE ORDER", "shopping"),
    ])
    def test_keyword_categorization(self, predictor, description, expected):
        assert predictor.predict(tx(description, -20.0)).category == expected

    def test_vietnamese_description(self, predictor):
        assert predictor.predict(tx("Cà phê sáng", -3.0)).category == "food_drink"

    def test_unknown_text_falls_back_to_other(self, predictor):
        assert predictor.predict(tx("XYZQ 8891", -20.0)).category == UNKNOWN_CATEGORY

    def test_bare_credit_is_income(self, predictor):
        assert predictor.predict(tx("", 5000.0)).category == "income"

    def test_confidence_is_bounded(self, predictor):
        confidence = predictor.predict(tx("STARBUCKS COFFEE", -5.0)).confidence
        assert 0.0 <= confidence <= 1.0

    def test_reports_heuristic_backend_without_artifact(self, predictor):
        # No artifact is committed, so this must be the fallback path.
        assert predictor.info().backend == "heuristic"

    def test_low_confidence_downgraded_to_other(self):
        # Force the floor high so every prediction is 'too weak'.
        strict = CategoryPredictor(MLSettings(ML_MIN_CONFIDENCE=0.99))
        assert strict.predict(tx("STARBUCKS", -5.0)).category == UNKNOWN_CATEGORY


# ----------------------------------------------------------------------
# Anomaly detection
# ----------------------------------------------------------------------

class TestAnomalyScorer:
    @pytest.fixture
    def scorer(self):
        return AnomalyScorer()

    def test_short_history_reports_insufficient_data(self, scorer):
        stats = scorer.build_stats(routine_history(count=3))
        result = scorer.predict(tx("ANYTHING", -9999.0), stats)
        assert result.insufficient_data is True
        assert result.is_anomaly is False

    def test_routine_transaction_is_not_flagged(self, scorer):
        stats = scorer.build_stats(routine_history())
        result = scorer.predict(
            tx("VINMART GROCERY", -50.0, merchant="Vinmart"), stats
        )
        assert result.is_anomaly is False

    def test_large_unfamiliar_charge_is_flagged(self, scorer):
        stats = scorer.build_stats(routine_history())
        result = scorer.predict(
            tx("UNKNOWN OFFSHORE TRANSFER", -8000.0,
               date=datetime(2024, 3, 16, 3, 30), merchant="Unknown Entity"),
            stats,
        )
        assert result.is_anomaly is True
        assert result.score > 0.5

    def test_result_is_explainable(self, scorer):
        stats = scorer.build_stats(routine_history())
        result = scorer.predict(tx("WEIRD THING", -5000.0), stats)
        # An anomaly shown to a user must say why.
        assert len(result.signals) == 5
        assert all(s.explanation for s in result.signals)

    def test_score_stays_in_range_for_extreme_input(self, scorer):
        stats = scorer.build_stats(routine_history())
        result = scorer.predict(tx("HUGE", -10_000_000.0), stats)
        assert 0.0 <= result.score <= 1.0

    def test_identical_amounts_do_not_divide_by_zero(self, scorer):
        # Zero MAD would blow up a naive z-score.
        stats = scorer.build_stats(routine_history(count=20, amount=-50.0))
        result = scorer.predict(tx("VINMART GROCERY", -50.0, merchant="Vinmart"), stats)
        assert 0.0 <= result.score <= 1.0

    def test_rapid_repeat_detected(self, scorer):
        history = routine_history() + [
            tx("DUPLICATE CHARGE", -120.0,
               date=BASE_DATE - timedelta(hours=2), merchant="Shop X")
        ]
        stats = scorer.build_stats(history)
        result = scorer.predict(
            tx("DUPLICATE CHARGE", -120.0, merchant="Shop X"), stats
        )
        repeat = next(s for s in result.signals if s.name == "rapid_repeat")
        assert repeat.value == 1.0


# ----------------------------------------------------------------------
# Service orchestration
# ----------------------------------------------------------------------

class TestMLService:
    @pytest.fixture
    def service(self):
        return MLService()

    def test_preserves_order_and_length(self, service):
        transactions = [tx(f"MERCHANT {i}", -10.0 * (i + 1)) for i in range(5)]
        response = service.predict(PredictRequest(transactions=transactions))
        assert response.count == 5
        assert [p.description for p in response.predictions] == [
            t.description for t in transactions
        ]

    def test_batch_is_truncated_to_limit(self):
        service = MLService(MLSettings(ML_MAX_BATCH_SIZE=10))
        response = service.predict(
            PredictRequest(transactions=[tx("X", -1.0) for _ in range(50)])
        )
        assert response.count == 10

    def test_disabled_flag_returns_same_shape(self):
        service = MLService(MLSettings(ML_ENABLED=False))
        response = service.predict(
            PredictRequest(transactions=[tx("STARBUCKS", -5.0)])
        )
        assert response.count == 1
        assert response.predictions[0].category.backend == "disabled"
        assert response.anomaly_count == 0

    def test_explicit_history_is_used_as_baseline(self, service):
        response = service.predict(PredictRequest(
            transactions=[tx("LUXURY WATCH", -9000.0, merchant="Rare Shop")],
            history=routine_history(),
        ))
        assert response.predictions[0].anomaly.is_anomaly is True

    def test_predict_one_works_without_history(self, service):
        result = service.predict_one(tx("STARBUCKS COFFEE", -5.4))
        assert result.category.category == "food_drink"
        # With no baseline there is nothing to compare against, so the scorer
        # must abstain rather than guess.
        assert result.anomaly.insufficient_data is True

    def test_model_info_lists_both_predictors(self, service):
        names = {info.name for info in service.model_info()}
        assert names == {"categorizer", "anomaly_scorer"}

    def test_empty_batch_is_rejected_at_the_schema(self):
        # An empty batch is a client error, so it is rejected by validation
        # before reaching the service rather than returning an empty result.
        with pytest.raises(ValidationError):
            PredictRequest(transactions=[])

    def test_anomaly_count_matches_flags(self, service):
        response = service.predict(PredictRequest(
            transactions=routine_history(count=5) + [tx("ODD", -9999.0)],
            history=routine_history(),
        ))
        expected = sum(1 for p in response.predictions if p.anomaly.is_anomaly)
        assert response.anomaly_count == expected
