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
def create_tables() -> None:
    """Crear todas las tablas registradas en Base.metadata."""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Tables created successfully.")
    except OperationalError as e:
        logger.error("Could not create tables: %s", e)
        raise


# ─────────────────────────────────────────
#  Health check
# ─────────────────────────────────────────
def check_db_connection() -> bool:
    """Verficar si la base de datos es accesible ejecutando una consulta simple."""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("Database connection OK.")
        return True
    except OperationalError as e:
        logger.error("Database connection failed: %s", e)
        return False


# ─────────────────────────────────────────
#  Dependency — FastAPI
# ─────────────────────────────────────────
def get_db():

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def get_async_db() -> AsyncSession:
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