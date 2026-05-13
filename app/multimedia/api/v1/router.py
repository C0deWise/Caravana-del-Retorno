from fastapi import APIRouter
from app.multimedia.api.v1.endpoints.multimedia_router import router as multimedia_router

router = APIRouter()

router.include_router(
    multimedia_router,
    prefix="/multimedia",
    tags=["Multimedia"],
)