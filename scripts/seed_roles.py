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

        # Verificar si ya existen roles
        result = await db.execute(select(Rol.ro_nombre))
        nombres_existentes = set(result.scalars().all())

        roles_a_crear = []
        for nombre in ROLES:
            if nombre not in nombres_existentes:
                db.add(Rol(ro_nombre=nombre))
                roles_a_crear.append(nombre)

        if roles_a_crear:
            await db.commit()
            logger.info("Roles insertados: %s", roles_a_crear)
        else:
            logger.info("Todos los roles ya existen en la base de datos.")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed_roles())