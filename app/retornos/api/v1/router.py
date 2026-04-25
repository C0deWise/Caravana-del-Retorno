"""
Router principal de la versión v1 de la API.
Agrupa y registra todos los routers de los módulos disponibles.
"""

from fastapi import APIRouter
from app.retornos.api.v1.endpoints.retorno_router import router as retorno_router, grupo_retorno_router

api_router = APIRouter()

api_router.include_router(retorno_router)
api_router.include_router(grupo_retorno_router)