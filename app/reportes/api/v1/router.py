from fastapi import APIRouter
from app.reportes.api.v1.endpoints.reportes_router import router as reportes_router

router = APIRouter()

router.include_router(
    reportes_router,
    prefix="/reportes",
    tags=["Reportes"],
)