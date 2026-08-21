from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.core.config import get_settings
from src.core.database import init_db
from src.api import transactions_router, health_router
from src.modules.chat import chat_router

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

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8080"],  # Frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health_router, prefix="/api/health", tags=["Health"])
app.include_router(transactions_router, prefix="/api/transactions", tags=["Transactions"])
# MODULE 6: LLM Chat Interface (self-contained in src/modules/chat)
app.include_router(chat_router, prefix="/api/chat", tags=["Chat"])


@app.get("/")
async def root():
    return {"message": "Wealify Financial Assistant API", "version": settings.APP_VERSION}
