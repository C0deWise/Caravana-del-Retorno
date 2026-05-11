from typing import Annotated, List
from fastapi import APIRouter, Depends, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.publicacion.servicios.publicacion_servicio import PublicacionServicio
from app.publicacion.esquemas.publicacion_esquema import PublicacionRespuesta, PublicacionCrear
from app.publicacion.repositorios.publicacion_repositorio import PublicacionRepositorio
from app.multimedia.repositorios.multimedia_repositorio import MultimediaRepositorio
from app.multimedia.servicios.multimedia_servicio import MultimediaServicio
from app.retornos.servicios.retorno_servicio import RetornoService
from app.usuarios.repository.usuario_repositorio import UsuarioRepositorio
from app.usuarios.services.usuario_servicio import UsuarioServicio
from app.publicacion.docs.docs_publicacion import crear_publicacion_docs, obtener_publicaciones_retorno_docs

def get_publicacion_servicio(db: Annotated[AsyncSession, Depends(get_db)]):
    publicacion_repositorio = PublicacionRepositorio(db)
    multimedia_repositorio = MultimediaRepositorio(db)
    multimedia_servicio = MultimediaServicio(multimedia_repositorio)
    retorno_servicio = RetornoService(db)
    usuario_repositorio = UsuarioRepositorio(db)
    usuario_servicio = UsuarioServicio(usuario_repositorio)
    return PublicacionServicio(
        repositorio=publicacion_repositorio,
        multimedia_servicio=multimedia_servicio,
        retorno_servicio=retorno_servicio,
        usuario_servicio=usuario_servicio
    )

router = APIRouter()

@router.post(
    "/crear-publicacion/",
    response_model=PublicacionRespuesta, **crear_publicacion_docs
)
async def crear_publicacion(
    retorno_id: Annotated[int, Form(...)],
    autor: Annotated[int, Form(...)],
    titulo: Annotated[str, Form(...)],
    resena: Annotated[str, Form(...)],
    archivos: Annotated[List[UploadFile], File(...)],
    servicio: Annotated[PublicacionServicio, Depends(get_publicacion_servicio)],
):
    datos_publicacion = PublicacionCrear(
        retorno=retorno_id,
        autor=autor,
        titulo=titulo,
        resena=resena
    )
    return await servicio.crear_publicacion(datos_publicacion, archivos)

@router.get(
    "/obtener-publicaciones-retorno/{retorno_id}/",
    response_model=List[PublicacionRespuesta], **obtener_publicaciones_retorno_docs
)
async def consultar_publicaciones_por_retorno(
    retorno_id: int,
    servicio: Annotated[PublicacionServicio, Depends(get_publicacion_servicio)],
):
    return await servicio.consultar_publicacion_por_retorno(retorno_id)
