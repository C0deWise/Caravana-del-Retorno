"""
router.py (api/v1/)
==================
Propósito: Enrutador principal del módulo de reportes.
          Incluye los endpoints para acceder a los diferentes tipos de reportes
          disponibles en la aplicación.
"""

from fastapi import APIRouter
from app.reportes.api.v1.endpoints.reportes_router import router as reportes_router

router = APIRouter()

router.include_router(
    reportes_router,
    prefix="/reportes",
    tags=["Reportes"],
)