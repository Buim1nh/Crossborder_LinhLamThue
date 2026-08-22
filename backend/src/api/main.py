from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.core.config import get_settings
from src.core.database import init_db
from src.api import (
    auth_router,
    health_router,
    subscriptions_router,
    transactions_router,
    upload_router,
)
from src.api.anomalies import router as anomalies_router

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan events."""
    # Startup
    await init_db()
    yield
    # Shutdown
    pass


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan,
)

# CORS configuration supporting Vercel deployments, custom domains, and local development
cors_origins = [
    origin.strip()
    for origin in settings.CORS_ORIGINS.split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins if cors_origins and "*" not in cors_origins else ["*"],
    allow_origin_regex=r"^https://.*\.vercel\.app$|^http://localhost(:\d+)?$|^http://127\.0\.0\.1(:\d+)?$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Include routers
app.include_router(health_router, prefix="/api/health", tags=["Health"])
app.include_router(auth_router, prefix="/api/auth", tags=["Authentication & Authorization"])
app.include_router(transactions_router, prefix="/api/transactions", tags=["Transactions"])
app.include_router(subscriptions_router, prefix="/api/subscriptions", tags=["Subscriptions"])
app.include_router(upload_router, prefix="/api/upload", tags=["Upload"])
app.include_router(anomalies_router, prefix="/api/anomalies", tags=["Anomalies"])
@app.get("/")
async def root():
    return {"message": "Wealify Financial Assistant API", "version": settings.APP_VERSION}
