from typing import AsyncGenerator
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from contextlib import contextmanager
from app.core.config import get_settings
import logging

logger = logging.getLogger(__name__)

settings = get_settings()


# ─────────────────────────────────────────
#  Engine
# ─────────────────────────────────────────
engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)

async_engine = create_async_engine(
    settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://"),
    echo=settings.DEBUG,
    pool_pre_ping=True,
)




# ─────────────────────────────────────────
#  Session
# ─────────────────────────────────────────
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
)

AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
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
        async with async_engine.begin() as conn:
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
        async with async_engine.connect() as conn:
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

@contextmanager
def get_db_context():
    """Administrador de contexto para obtener la sesion de la base de datos afuera del contexto de FastAPI."""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()