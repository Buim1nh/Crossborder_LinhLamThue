"""
MODULE 7 - Step 2: ARTIFACT LOADING.

A tiny model registry that loads serialized estimators from disk exactly once
and caches them in-process.

Two properties matter here:

1. Loading is LAZY and CACHED. Deserializing an sklearn pipeline costs tens of
   milliseconds; doing it per-request under an async server would be a
   self-inflicted bottleneck.
2. Loading NEVER raises. A missing artifact or a missing `joblib` is an
   expected state (fresh checkout, CI), not an error. The caller inspects
   `.loaded` and falls back to heuristics.
"""
import logging
import threading
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)


class LoadedModel:
    """An artifact load attempt: either a live estimator or a recorded reason."""

    def __init__(
        self,
        name: str,
        path: Path,
        estimator: Any = None,
        error: Optional[str] = None,
    ):
        self.name = name
        self.path = path
        self.estimator = estimator
        self.error = error

    @property
    def loaded(self) -> bool:
        return self.estimator is not None

    def __repr__(self) -> str:  # pragma: no cover - debugging aid
        status = "loaded" if self.loaded else f"unavailable ({self.error})"
        return f"<LoadedModel {self.name}: {status}>"


class ModelRegistry:
    """Process-wide cache of deserialized model artifacts."""

    def __init__(self) -> None:
        self._cache: dict[str, LoadedModel] = {}
        # Guards the cache: FastAPI may serve concurrent requests, and two
        # threads racing to load the same artifact would double the work.
        self._lock = threading.Lock()

    def load(self, name: str, path: Path) -> LoadedModel:
        """
        Return the cached artifact for `name`, loading it on first use.

        Never raises: failures are captured on the returned object.
        """
        cache_key = f"{name}:{path}"

        cached = self._cache.get(cache_key)
        if cached is not None:
            return cached

        with self._lock:
            # Re-check: another thread may have populated it while we waited.
            cached = self._cache.get(cache_key)
            if cached is not None:
                return cached

            result = self._load_uncached(name, path)
            self._cache[cache_key] = result
            return result

    def _load_uncached(self, name: str, path: Path) -> LoadedModel:
        if not path.exists():
            msg = f"artifact not found at {path}"
            logger.info("ML model '%s' unavailable: %s - using fallback", name, msg)
            return LoadedModel(name, path, error=msg)

        try:
            import joblib
        except ImportError:
            msg = "joblib not installed (pip install joblib scikit-learn)"
            logger.info("ML model '%s' unavailable: %s - using fallback", name, msg)
            return LoadedModel(name, path, error=msg)

        try:
            estimator = joblib.load(path)
        except Exception as exc:  # noqa: BLE001 - must not break inference
            # A corrupt or version-mismatched pickle should degrade to the
            # heuristic path, not take down the API.
            msg = f"failed to deserialize: {type(exc).__name__}: {exc}"
            logger.warning("ML model '%s' failed to load: %s", name, msg)
            return LoadedModel(name, path, error=msg)

        logger.info("ML model '%s' loaded from %s", name, path)
        return LoadedModel(name, path, estimator=estimator)

    def clear(self) -> None:
        """Drop all cached artifacts. Used by tests and hot-reload flows."""
        with self._lock:
            self._cache.clear()


# Single shared registry for the process.
_registry = ModelRegistry()


def get_registry() -> ModelRegistry:
    return _registry
