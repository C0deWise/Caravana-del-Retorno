




from fastapi import APIRouter

from app.notificaciones.api.v1.endpoints.router_notificaciones import router as router_notificaciones


router = APIRouter()

router.include_router(
    prefix="/notificaciones",
    tags=["Notificaciones"],
    router=router_notificaciones
)
