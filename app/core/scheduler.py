
import logging

from apscheduler.schedulers.background import BackgroundScheduler
from fastapi import Depends
from sqlalchemy.ext import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from app.colonias.repositories.solicitud_colonia_repository import SolicitudColoniaRepository
from app.core.database import AsyncSessionLocal, SessionLocal, get_async_db  
from app.colonias.services.solicitud_colonias_services import SolicitudColoniaService

logger = logging.getLogger(__name__)

_scheduler = BackgroundScheduler()

async def _async_expirar_solicitudes() -> None:
    try:
        async with AsyncSessionLocal() as db:
            repositorio = SolicitudColoniaRepository(db)
            servicio = SolicitudColoniaService(repositorio)
            total = await servicio.expirar_solicitudes_vencidas()
            logger.info(f"[Scheduler] Solicitudes expiradas: {total}")
    except Exception:
        logger.exception("[Scheduler] Error al expirar solicitudes.")

def _job_expirar_solicitudes() -> None:
    """Job diario: wrapper síncrono que ejecuta la corutina asíncrona."""
    asyncio.run(_async_expirar_solicitudes())


def start() -> None:
    """Registra los jobs e inicia el scheduler. Llamar en el lifespan startup."""
    _scheduler.add_job(
        _job_expirar_solicitudes,
        trigger="cron",
        hour=0,
        minute=0,
        id="expirar_solicitudes_colonia",
        replace_existing=True,
    )
    _scheduler.start()
    logger.info("[Scheduler] Iniciado.")


def shutdown() -> None:
    """Detiene el scheduler. Llamar en el lifespan shutdown."""
    if _scheduler.running:
        _scheduler.shutdown()
        logger.info("[Scheduler] Detenido.")