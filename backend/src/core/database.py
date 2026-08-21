from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from src.core.config import get_settings

settings = get_settings()

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
)

async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncSession:
    """Dependency for getting async database session."""
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    """Initialize database tables and run migrations."""
    # Ensure all models are imported before creating tables
    import src.models  # noqa: F401

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Run pending migrations
    await _run_migrations()


async def _run_migrations():
    """Run schema migrations (add missing columns to existing tables)."""
    from sqlalchemy import text

    async with engine.begin() as conn:
        # Get existing columns for transactions table
        result = await conn.execute(
            text("PRAGMA table_info(transactions)")
        )
        existing_cols = {row[1] for row in result.fetchall()}

        migrations = []

        if "user_id" not in existing_cols:
            migrations.append(
                text("ALTER TABLE transactions ADD COLUMN user_id INTEGER NOT NULL DEFAULT 0")
            )

        for migration in migrations:
            try:
                await conn.execute(migration)
            except Exception as exc:
                # Log but don't fail startup — table might already have the column
                print(f"[migration] skipped: {exc}")
