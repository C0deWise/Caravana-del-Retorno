from typing import Annotated

from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.retornos.servicios.retorno_servicio import RetornoService
from app.multimedia.esquemas.multimedia_esquemas import MultimediaRespuesta
from app.multimedia.repositorios.multimedia_repositorio import MultimediaRepositorio
from app.multimedia.servicios.multimedia_servicio import MultimediaServicio
from app.multimedia.docs.docs_multimedia import cargar_contenido_multimedia_docs

router = APIRouter()

def get_multimedia_servicio(db: Annotated[AsyncSession, Depends(get_db)]) -> MultimediaServicio:
    repositorio = MultimediaRepositorio(db)
    retorno_servicio = RetornoService(db)
    return MultimediaServicio(repositorio, retorno_servicio)

@router.post(
    "/cargar-multimedia/{retorno_codigo}",
    tags=["Multimedia"],
    response_model=list[MultimediaRespuesta], **cargar_contenido_multimedia_docs
)
async def cargar_contenido_multimedia(
    retorno_codigo: int, 
    archivos: Annotated[list[UploadFile], File(...)], 
    servicio: Annotated[MultimediaServicio, Depends(get_multimedia_servicio)]):
    return await servicio.cargar_archivos_multimedia(retorno_codigo, archivos)