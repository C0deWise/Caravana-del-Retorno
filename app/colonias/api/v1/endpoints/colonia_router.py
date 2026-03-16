from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.usuarios.api.v1.usuario_router import get_usuario_servicio
from app.colonias.schemas.colonia_schemas import ColoniaCreate, ColoniaResponse
from app.colonias.schemas.colonia_solicitud_schemas import SolicitudColoniaCrear, SolicitudColoniaRespuesta
from app.colonias.services.colonia_services import service_crear_colonia, service_obtener_colonias
from app.colonias.services.solicitud_colonias_services import SolicitudColoniaService
from app.usuarios.services.usuario_servicio import UsuarioServicio
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
    response_model = SolicitudColoniaRespuesta,
    status_code = status.HTTP_201_CREATED,
    summary = "Crear una solicitud de ingreso a una colonia",
    description = "Crea una nueva solicitud de ingreso a una colonia con el código de usuario y el código de colonia",
)
def crear_solicitud_colonia(datos: SolicitudColoniaCrear, db: Session = Depends(get_db),  servicio: UsuarioServicio = Depends(get_usuario_servicio)):
    if not servicio.existe_usuario("us_codigo", datos.codigo_usuario):
            raise ValueError(f"El usuario con código {datos.codigo_usuario} no existe.")
    return SolicitudColoniaService().crear_solicitud(db, datos)

@router.get(
    "/solicitudes-pendientes/{cod_colonia}",
    response_model = list[SolicitudColoniaRespuesta],
    status_code = status.HTTP_200_OK,
    summary = "Obtener solicitudes de ingreso pendientes",
    description = "Obtiene una lista de todas las solicitudes de ingreso a colonias que están pendientes de revisión",
)
def obtener_solicitudes_pendientes_colonia(cod_colonia: int, db: Session = Depends(get_db)):
    return SolicitudColoniaService().obtener_solicitudes_pendientes_colonia(db, cod_colonia)


@router.get("/solicitudes-recientes/{cod_colonia}",
            response_model = list[SolicitudColoniaRespuesta],
    status_code = status.HTTP_200_OK,
    summary = "Obtener solicitudes de ingreso recientes",
    description = "Obtiene una lista de las solicitudes de ingreso a colonias que han sido creadas en los últimos 30 días",
)
def obtener_solicitudes_recientes_colonia(cod_colonia: int, db: Session = Depends(get_db)):
    return SolicitudColoniaService().obtener_solicitudes_recientes_colonia(db, cod_colonia)


@router.get("/solicitudes-recientes-usuario/{cod_usuario}",
            response_model = list[SolicitudColoniaRespuesta],
    status_code = status.HTTP_200_OK,
    summary = "Obtener solicitudes de ingreso recientes por usuario",
    description = "Obtiene una lista de las solicitudes de ingreso a colonias que han sido creadas en los últimos 30 días por un usuario específico",
)
def obtener_solicitudes_recientes_usuario(cod_usuario: int, db: Session = Depends(get_db)):
    return SolicitudColoniaService().obtener_solicitudes_recientes_usuario(db, cod_usuario)