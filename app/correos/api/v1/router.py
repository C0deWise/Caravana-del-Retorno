"""
Agrupa todos los routers v1 del módulo `correos`. Facilita agregar más
endpoints (ej. notificaciones, bienvenida) sin tocar el `main.py` del monolito.
"""
from fastapi import APIRouter

from app.correos.api.v1.email import router as email_router

router = APIRouter()
router.include_router(email_router)
