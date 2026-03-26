from fastapi import APIRouter
from app.colonias.api.v1.endpoints.colonia_router import router as colonia_router

router = APIRouter()

router.include_router(
    colonia_router,
    prefix="/colonias",
    tags=["Colonias"],
)