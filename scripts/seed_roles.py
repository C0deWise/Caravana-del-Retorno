import asyncio
import logging
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import get_settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s — %(name)s — %(levelname)s — %(message)s",
)
logger = logging.getLogger(__name__)

settings = get_settings()

ROLES = ["usuario", "lider", "admin"]


async def seed_roles() -> None:
    # Render suele entregar postgres://, asyncpg requiere postgresql+asyncpg://
    db_url = settings.DATABASE_URL
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql+asyncpg://", 1)
    elif db_url.startswith("postgresql://"):
        db_url = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)
    else:
        # Por si ya viene con el driver o es otro formato
        db_url = db_url.replace("://", "+asyncpg://", 1) if "+asyncpg" not in db_url else db_url

    engine = create_async_engine(db_url, echo=False)
    async_session = async_sessionmaker(bind=engine, expire_on_commit=False)

    async with async_session() as db:
        # Importar aquí para evitar imports circulares
        from app.usuarios.models.usuario import Rol

        # INSERT ... ON CONFLICT DO NOTHING garantiza idempotencia a nivel de BD
        stmt = (
            insert(Rol)
            .values([{"ro_nombre": nombre} for nombre in ROLES])
            .on_conflict_do_nothing(index_elements=["ro_nombre"])
        )
        await db.execute(stmt)
        await db.commit()
        logger.info("Seed de roles completado (duplicados ignorados automáticamente).")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed_roles())