from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from app.colonias.repositories.solicitud_colonia_repository import SolicitudColoniaRepository
from app.core.database import get_async_db, get_db
from app.usuarios.api.v1.usuario_router import get_usuario_servicio
from app.colonias.schemas.colonia_schemas import ColoniaCreate, ColoniaResponse
from app.colonias.schemas.colonia_solicitud_schemas import SolicitudColoniaCrear, SolicitudColoniaRespuesta
from app.colonias.services.colonia_services import service_crear_colonia, service_obtener_colonias
from app.colonias.services.solicitud_colonias_services import SolicitudColoniaService
from app.usuarios.services.usuario_servicio import UsuarioServicio

from app.colonias.docs.docs_solicitud_colonia import (
    crear_solicitud_docs,
    obtener_solicitudes_pendientes_docs,
    obtener_solicitudes_recientes_colonia_docs,
    obtener_solicitudes_recientes_usuario_docs,
)

def get_solicitud_colonia_servicio(db: AsyncSession = Depends(get_async_db)) -> SolicitudColoniaRepository:
    repositorio = SolicitudColoniaRepository(db)
    return SolicitudColoniaService(repositorio)

router = APIRouter()

@router.post(
    "/",
    response_model = ColoniaResponse,
    status_code = status.HTTP_201_CREATED,
    summary = "Crear una colonia",
    description = "Crea una nueva colonia con país, departamento y ciudad",
)
def crear_colonia(datos: ColoniaCreate, db: Session = Depends(get_db)):
    return service_crear_colonia(db, datos)

@router.get(
    "/",
    response_model = list[ColoniaResponse],
    status_code = status.HTTP_200_OK,
    summary = "Obtener todas las colonias",
    description = "Obtiene una lista de todas las colonias registradas en el sistema",
)
def obtener_colonias(db: Session = Depends(get_db)):
    return service_obtener_colonias(db)

@router.post(
    "/crear-solicitud",
    response_model=SolicitudColoniaRespuesta, **crear_solicitud_docs
)
async def crear_solicitud_colonia(
    datos: SolicitudColoniaCrear,
    servicio_usuario: UsuarioServicio = Depends(get_usuario_servicio),
    servicio: SolicitudColoniaService = Depends(get_solicitud_colonia_servicio),
):
    if not servicio_usuario.existe_usuario("us_codigo", datos.codigo_usuario):
        raise ValueError(f"El usuario con código {datos.codigo_usuario} no existe.")
    return await servicio.crear_solicitud(datos)


@router.get(
    "/solicitudes-pendientes/{cod_colonia}",
    response_model=list[SolicitudColoniaRespuesta], **obtener_solicitudes_pendientes_docs
)
async def obtener_solicitudes_pendientes_colonia(
    cod_colonia: int,
    servicio: SolicitudColoniaService = Depends(get_solicitud_colonia_servicio),
):
    return await servicio.obtener_solicitudes_pendientes_colonia(cod_colonia)


@router.get(
    "/solicitudes-recientes/{cod_colonia}",
    response_model=list[SolicitudColoniaRespuesta], **obtener_solicitudes_recientes_colonia_docs
)
async def obtener_solicitudes_recientes_colonia(
    cod_colonia: int,
    servicio: SolicitudColoniaService = Depends(get_solicitud_colonia_servicio),
):
    return await servicio.obtener_solicitudes_recientes_colonia(cod_colonia)


@router.get(
    "/solicitudes-recientes-usuario/{cod_usuario}",
    response_model=list[SolicitudColoniaRespuesta], **obtener_solicitudes_recientes_usuario_docs
)
async def obtener_solicitudes_recientes_usuario(
    cod_usuario: int,
    servicio: SolicitudColoniaService = Depends(get_solicitud_colonia_servicio),
):
    return await servicio.obtener_solicitudes_recientes_usuario(cod_usuario)