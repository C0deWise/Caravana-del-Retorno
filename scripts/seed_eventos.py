import asyncio
import logging
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import select

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

EVENTOS = [
    {
        "ev_nombre": "Salida de grupo de retorno",
        "ev_descripcion": "Se genera cuando alguien se sale de un grupo de retorno"
    },
    {
        "ev_nombre": "Salida de retorno",
        "ev_descripcion": "Se genera cuando alguien se sale de un retorno"
    },
    {
        "ev_nombre": "Designación de líder",
        "ev_descripcion": "Se genera cuando una persona es establecida como líder"
    },
    {
        "ev_nombre": "Revocación de líder",
        "ev_descripcion": "Se genera cuando a una persona se le revoca el rol de líder"
    },
    {
        "ev_nombre": "Aceptación en colonia",
        "ev_descripcion": "Se genera cuando una persona es aceptada en una colonia"
    },
    {
        "ev_nombre": "Rechazo en colonia",
        "ev_descripcion": "Se genera cuando una persona es rechazada de una colonia"
    },
    {
        "ev_nombre": "Cancelación de grupo de retorno",
        "ev_descripcion": "Se genera cuando se cancela un grupo de retorno"
    },
    {
        "ev_nombre": "Registro de grupo a retorno",
        "ev_descripcion": "Se genera cuando un grupo de retorno se registra a un retorno"
    },
    {
        "ev_nombre": "Edición de registro de grupo",
        "ev_descripcion": "Se genera cuando se edita el registro de un grupo de retorno"
    },
    {
        "ev_nombre": "Desactivación de colonia",
        "ev_descripcion": "Se genera cuando se desactiva una colonia"
    },
    {
        "ev_nombre": "Solicitud ingreso a colonia",
        "ev_descripcion": "Se genera cuando un usuario crea una solicitud de ingreso a una colonia"
    },
    {
        "ev_nombre": "Solicitud de parentesco",
        "ev_descripcion": "Se genera cuando un usuario crea una solicitud de parentesco"
    },
    {
        "ev_nombre": "Aceptación de parentesco",
        "ev_descripcion": "Se genera cuando un usuario acepta una solicitud de parentesco"
    },
    {
        "ev_nombre": "Rechazo de parentesco",
        "ev_descripcion": "Se genera cuando un usuario rechaza una solicitud de parentesco"
    },
]


async def seed_eventos() -> None:
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
        from app.notificaciones.models.notificacion_model import Evento

        eventos_creados = 0
        eventos_existentes = 0
        
        for evento_data in EVENTOS:
            # Verificar si el evento ya existe
            stmt = select(Evento).where(Evento.ev_nombre == evento_data["ev_nombre"])
            resultado = await db.execute(stmt)
            evento_existente = resultado.scalars().first()
            
            if evento_existente:
                eventos_existentes += 1
                logger.info(f"Evento '{evento_data['ev_nombre']}' ya existe, saltando...")
            else:
                # Crear el evento
                nuevo_evento = Evento(
                    ev_nombre=evento_data["ev_nombre"],
                    ev_descripcion=evento_data["ev_descripcion"]
                )
                db.add(nuevo_evento)
                eventos_creados += 1
        
        if eventos_creados > 0:
            await db.commit()
            logger.info(f"Seed de eventos completado. Creados: {eventos_creados}, Existentes: {eventos_existentes}")
        else:
            logger.info(f"Seed de eventos completado. Todos los eventos ya existen. Existentes: {eventos_existentes}")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed_eventos())
