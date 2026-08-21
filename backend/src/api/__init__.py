from src.api.health import router as health_router
from src.api.auth import router as auth_router
from src.api.transactions import router as transactions_router
from src.api.subscriptions import router as subscriptions_router
from src.api.upload import router as upload_router

__all__ = ["health_router", "auth_router", "transactions_router", "subscriptions_router", "upload_router"]
