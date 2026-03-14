
import logging

from apscheduler.schedulers.background import BackgroundScheduler

from app.core.database import SessionLocal  # ajusta según tu proyecto
from app.colonias.services.solicitud_colonias_services import SolicitudColoniaService

logger = logging.getLogger(__name__)

_scheduler = BackgroundScheduler()


def _job_expirar_solicitudes() -> None:
    """Job diario: expira solicitudes pendientes con más de 30 días."""
    db = SessionLocal()
    try:
        total = SolicitudColoniaService().expirar_solicitudes_vencidas(db)
        logger.info(f"[Scheduler] Solicitudes expiradas: {total}")
    except Exception:
        logger.exception("[Scheduler] Error al expirar solicitudes.")
    finally:
        db.close()


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