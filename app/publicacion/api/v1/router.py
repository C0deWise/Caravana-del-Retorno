from fastapi import APIRouter
from app.publicacion.api.v1.endpoints.publicacion_router import router as publicacion_router

router = APIRouter()

router.include_router(
    publicacion_router,
    prefix="/publicacion",
    tags=["Publicacion"],
)