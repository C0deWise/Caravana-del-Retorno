"""
    router.py - Router principal para la API de colonias (v1).
    Este módulo define el router principal para la versión 1 de la API de colonias
"""

from fastapi import APIRouter
from app.colonias.api.v1.endpoints.colonia_router import router as colonia_router

router = APIRouter()

router.include_router(
    colonia_router,
    prefix="/colonias",
    tags=["Colonias"],
)