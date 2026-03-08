import asyncio
import logging
from sqlalchemy import select
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
    engine = create_async_engine(
        settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://"),
        echo=False,
    )

    async_session = async_sessionmaker(bind=engine, expire_on_commit=False)

    async with async_session() as db:
        # Importar aquí para evitar imports circulares
        from app.usuarios.models.usuario import Rol

        # Verificar si ya existen roles
        result = await db.execute(select(Rol))
        existentes = result.scalars().all()

        if existentes:
            logger.info("Los roles ya existen, seed omitido.")
            await engine.dispose()
            return

        # Insertar roles
        for nombre in ROLES:
            db.add(Rol(ro_nombre=nombre))

        await db.commit()
        logger.info("Roles insertados: %s", ROLES)

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed_roles())