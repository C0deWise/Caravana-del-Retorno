"""
Scheduler de tareas periódicas.

Usa APScheduler para ejecutar jobs en segundo plano.
Instala la dependencia con:
    pip install apscheduler

Registra el scheduler en tu main.py:

    from app.scheduler import scheduler
    from contextlib import asynccontextmanager
    from fastapi import FastAPI

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        scheduler.start()
        yield
        scheduler.shutdown()

    app = FastAPI(lifespan=lifespan)
"""

import logging

from apscheduler.schedulers.background import BackgroundScheduler

from app.core.database import SessionLocal  # ajusta según tu proyecto
from app.colonias.services.solicitud_colonis_services import SolicitudColoniaService

logger = logging.getLogger(__name__)


def job_expirar_solicitudes() -> None:
    """Job diario: expira solicitudes pendientes con más de 30 días."""
    db = SessionLocal()
    try:
        total = SolicitudColoniaService().expirar_solicitudes_vencidas(db)
        logger.info(f"[Scheduler] Solicitudes expiradas: {total}")
    except Exception:
        logger.exception("[Scheduler] Error al expirar solicitudes.")
    finally:
        db.close()


scheduler = BackgroundScheduler()

# Se ejecuta todos los días a las 00:00
scheduler.add_job(
    job_expirar_solicitudes,
    trigger="cron",
    hour=0,
    minute=0,
    id="expirar_solicitudes_colonia",
    replace_existing=True,
)