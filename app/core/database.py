from typing import AsyncGenerator
from sqlalchemy import text
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.core.config import get_settings
import logging

logger = logging.getLogger(__name__)

settings = get_settings()


# ─────────────────────────────────────────
#  Engine
# ─────────────────────────────────────────
engine = create_async_engine(
    settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://"),
    echo=settings.DEBUG,
    pool_pre_ping=True,
)


# ─────────────────────────────────────────
#  Session
# ─────────────────────────────────────────
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
)
# ─────────────────────────────────────────
#  Base model
# ─────────────────────────────────────────
class Base(DeclarativeBase):
    pass


# ─────────────────────────────────────────
#  Table creation
# ─────────────────────────────────────────
async def create_tables() -> None:
    """Crear todas las tablas registradas en Base.metadata."""
    try:
        logger.info("Tablas registradas: %s", list(Base.metadata.tables.keys()))
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Tables created successfully.")
    except OperationalError as e:
        logger.error("Could not create tables: %s", e)
        raise


# ─────────────────────────────────────────
#  Health check
# ─────────────────────────────────────────
async def check_db_connection() -> bool:
    """Verficar si la base de datos es accesible ejecutando una consulta simple."""
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        logger.info("Database connection OK.")
        return True
    except OperationalError as e:
        logger.error("Database connection failed: %s", e)
        return False


# ─────────────────────────────────────────
#  Dependency — FastAPI
# ─────────────────────────────────────────
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session