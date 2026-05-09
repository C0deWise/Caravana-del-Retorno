"""
Endpoints HTTP para el módulo Retorno.
Expone operaciones de creación y consulta bajo el prefijo /retornos,
y operaciones de grupo de retorno bajo el prefijo /grupoRetorno,
con documentación Swagger integrada.
"""

from typing import Annotated

from app.retornos.esquemas.registro_retorno_esquema import RegistroRetornoCrear, RegistroRetornoDarseDeBaja, RegistroRetornoDarseDeBajaRespuesta, RegistroRetornoRespuesta
from app.retornos.esquemas.solicitud_retorno_grupo_esquema import SolicitudRetornoGrupoLiderRespuesta, SolicitudRetornoGrupoRespuesta, SolicitudRetornoGrupoUsuarioRespuesta
from app.retornos.repositorios.grupo_retorno_repositorio import GrupoRetornoRepositorio
from app.retornos.repositorios.registro_retorno_grupo_repositorio import RegistroRetornoGrupoRepositorio
from app.retornos.repositorios.registro_retorno_repositorio import RegistroRetornoRepositorio
from app.retornos.repositorios.retorno_grupo_usuario_repositorio import RetornoGrupoUsuarioRepositorio
from app.retornos.repositorios.persona_repositorio import PersonaRepositorio
from app.retornos.repositorios.retorno_repositorio import RetornoRepository
from app.retornos.repositorios.solicitud_grupo_retorno_repositorio import SolicitudGrupoRetornoRepositorio
from app.retornos.servicios.grupo_retorno_servicio import GrupoRetornoServicio
from app.retornos.servicios.registro_retorno_grupo_servicio import RegistroRetornoGrupoServicio
from app.retornos.servicios.registro_retorno_servicio import RegistroRetornoServicio
from app.retornos.esquemas.solicitud_grupo_retorno_esquema import SolicitudGrupoRetornoRespuesta, SolicitudGrupoRetornoEstado
from app.retornos.esquemas.grupo_retorno_esquema import GrupoRetornoCrear, GrupoRetornoRespuesta
from app.retornos.esquemas.registro_retorno_grupo_esquema import RegistroRetornoGrupoCrear, RegistroRetornoGrupoRespuesta
from app.usuarios.repository.usuario_repositorio import UsuarioRepositorio
from app.usuarios.services.usuario_servicio import UsuarioServicio
from app.usuarios.schemas.usuario_esquemas import UsuarioSalida
from fastapi import APIRouter, Depends, status, HTTPException, Body
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Annotated
from app.core.database import get_db
from app.retornos.esquemas.retorno_esquemas import RetornoCreate, RetornoResponse
from app.retornos.servicios.retorno_servicio import RetornoService
from app.usuarios.repository.parentesco_repositorio import ParentescoRepositorio
from app.retornos.esquemas.solicitud_grupo_retorno_esquema import SolicitudGrupoRetornoRespuesta, SolicitudGrupoRetornoEstado
router = APIRouter(
    prefix="/retornos",
    tags=["Retornos"],
)

grupo_retorno_router = APIRouter(
    prefix="/grupoRetorno",
    tags=["Grupos de Retorno"],
)

def obtener_registro_retorno_servicio(db: Annotated[AsyncSession, Depends(get_db)]) -> RegistroRetornoServicio:
    repositorio = RegistroRetornoRepositorio(db)
    retorno_repositorio = RetornoRepository(db)
    
    usuario_servicio = UsuarioServicio(UsuarioRepositorio(db), ParentescoRepositorio(db))
    
    return RegistroRetornoServicio(
        repositorio,
        retorno_repositorio,
        usuario_servicio
    )

def obtener_registro_retorno_grupo_servicio(db: Annotated[AsyncSession, Depends(get_db)]):
    repositorio_registro_grupo = RegistroRetornoGrupoRepositorio(db)
    repositorio_grupo = GrupoRetornoRepositorio(db)
    repositorio_retorno = RetornoRepository(db)
    repositorio_usuario_grupo = RetornoGrupoUsuarioRepositorio(db)
    repositorio_persona = PersonaRepositorio(db) # Instanciar PersonaRepositorio
    return RegistroRetornoGrupoServicio(
        repositorio_registro_grupo, repositorio_grupo, repositorio_retorno, repositorio_usuario_grupo, repositorio_persona
    )

def obtener_grupo_retorno_servicio(db: Annotated[AsyncSession, Depends(get_db)]):
    repositorio_retorno = RetornoRepository(db)
    repositorio_grupos = GrupoRetornoRepositorio(db)
    repositorio_solicitudes = SolicitudGrupoRetornoRepositorio(db)
    repositorio_usuario_grupo = RetornoGrupoUsuarioRepositorio(db)
    repositorio_usuario = UsuarioRepositorio(db)
    repositorio_registro_individual = RegistroRetornoRepositorio(db)
    repositorio_registro_grupo = RegistroRetornoGrupoRepositorio(db)
    return GrupoRetornoServicio(
        repositorio_retorno,
        repositorio_grupos,
        repositorio_solicitudes,
        repositorio_usuario_grupo,
        repositorio_usuario,
        repositorio_registro_individual,
        repositorio_registro_grupo
    )

def obtener_retorno_servicio(db: Annotated[AsyncSession, Depends(get_db)]) -> RetornoService:
    return RetornoService(db)


@router.post(
    "/",
    response_model=RetornoResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un nuevo retorno",
    description=(
        "Crea un nuevo registro de retorno. "
        "El año no puede ser anterior al actual ni estar ya asociado a otro retorno."
    ),
    responses={
        409: {
            "description": "Ya existe un evento de El Retorno para el año seleccionado.",
            "content": {"application/json": {"example": {"detail": "Ya existe un evento de El Retorno para el año seleccionado: 2024."}}},
        },
        422: {
            "description": "Año anterior al año actual del sistema.",
            "content": {"application/json": {"example": {"detail": "No es posible crear un evento de El Retorno en un año anterior al actual."}}},
        },
    },
)
async def crear_retorno(data: RetornoCreate, servicio: Annotated[RetornoService, Depends(obtener_retorno_servicio)]):
    return await servicio.crear_retorno(data)


@router.get(
    "/",
    response_model=list[RetornoResponse],
    summary="Listar todos los retornos",
    description="Obtiene el listado completo de retornos registrados en el sistema.",
)
async def listar_retornos(servicio: Annotated[RetornoService, Depends(obtener_retorno_servicio)]):
    return await servicio.listar_retornos()


@router.get(
    "/{codigo}",
    response_model=RetornoResponse,
    summary="Obtener retorno por código",
    description="Busca y retorna un retorno específico usando su código primario. Retorna 404 si no existe.",
)
async def obtener_retorno(codigo: int, servicio: Annotated[RetornoService, Depends(obtener_retorno_servicio)]):
    return await servicio.obtener_retorno(codigo)

@router.post(
    "/registro",
    response_model=RegistroRetornoRespuesta,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar participación en un retorno",
    description=(
        "Crea un nuevo registro de participación para un usuario en un retorno específico. "
        "Cada usuario solo puede registrar una participación por retorno."
    ),
    responses={
        409: {
            "description": "El usuario ya tiene un registro para este retorno.",
            "content": {"application/json": {"example": {"detail": "El usuario ya tiene un registro para este retorno."}}},
        },
        422: {
            "description": "Datos de entrada inválidos.",
            "content": {"application/json": {"example": {"detail": "Datos de entrada inválidos."}}},
        },
    },
)
async def inscribir_usuario_en_retorno(registro: RegistroRetornoCrear, servicio: Annotated[RegistroRetornoServicio, Depends(obtener_registro_retorno_servicio)]):
    return await servicio.crear_registro_retorno(registro)


@router.delete(
    "/darse-de-baja",
    response_model= RegistroRetornoDarseDeBajaRespuesta,
    summary="Darse de baja de un retorno",
    status_code=status.HTTP_200_OK,
    description="Permite a un usuario darse de baja de un retorno específico.",
)
async def darse_de_baja(datos: RegistroRetornoDarseDeBaja, servicio: Annotated[RegistroRetornoServicio, Depends(obtener_registro_retorno_servicio)]):
    resultado = await servicio.darse_de_baja(datos)
    if resultado:
        return RegistroRetornoDarseDeBajaRespuesta(mensaje=f"El usuario {datos.usuario} ha sido dado de baja exitosamente del retorno {datos.retorno}.")
@grupo_retorno_router.post(
    "/",
    response_model=GrupoRetornoRespuesta,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un nuevo grupo de retorno",
    description="Crea un nuevo grupo de retorno asignando un líder.",
    responses={
        404: {
            "description": "El líder especificado no existe.",
            "content": {"application/json": {"example": {"detail": "Usuario con ID 123 no encontrado"}}},
        },
    },
)
async def crear_grupo_retorno_endpoint(
    data: GrupoRetornoCrear,
    servicio: Annotated[GrupoRetornoServicio, Depends(obtener_grupo_retorno_servicio)]
):
    """
    Endpoint para crear un nuevo grupo de retorno.
    """
    return await servicio.crear_grupo_retorno(data)


@grupo_retorno_router.get(
    "/lider/{us_codigo_lider}",
    response_model=List[GrupoRetornoRespuesta],
    summary="Obtener grupos de retorno por código de líder",
    description="Obtiene todos los grupos de retorno liderados por un usuario específico.",
    responses={
        404: {
            "description": "El líder especificado no existe.",
            "content": {"application/json": {"example": {"detail": "Usuario con ID 123 no encontrado"}}},
        },
    },
)
async def obtener_grupos_por_lider_endpoint(
    us_codigo_lider: int,
    servicio: Annotated[GrupoRetornoServicio, Depends(obtener_grupo_retorno_servicio)]
):
    """
    Endpoint para obtener grupos de retorno por el código del líder.
    """
    return await servicio.obtener_grupos_por_lider_id(us_codigo_lider)


@grupo_retorno_router.get(
    "/{gr_codigo}/lider",
    response_model=UsuarioSalida, 
    summary="Obtener líder de grupo por código de grupo",
    description="Obtiene los detalles del líder de un grupo de retorno específico.",
    responses={
        404: {
            "description": "El grupo de retorno no existe.",
            "content": {"application/json": {"example": {"detail": "Grupo de retorno con código 123 no encontrado"}}},
        },
    },
)
async def obtener_lider_de_grupo_endpoint(
    gr_codigo: int,
    servicio: Annotated[GrupoRetornoServicio, Depends(obtener_grupo_retorno_servicio)]
):
    return await servicio.obtener_lider_por_grupo_id(gr_codigo)

@grupo_retorno_router.post(
    "/solicitar-miembro",
    response_model=SolicitudGrupoRetornoRespuesta,
    status_code=status.HTTP_201_CREATED,
    summary="Enviar solicitud individual a un usuario",
    description="El líder envía una solicitud a un usuario registrado para que se una a su grupo de retorno.",
    responses={
        404: {"description": "Usuario o Grupo no encontrado."},
        201: {
            "description": "Solicitud enviada exitosamente.",
            "content": {
                "application/json": {
                    "example": {
                        "solgr_codigo": 1,
                        "us_codigo": 123,
                        "gr_codigo": 456,
                        "solgr_time_stamp": "2026-04-25T03:45:31.000000+00:00",
                        "solgr_estado": SolicitudGrupoRetornoEstado.PENDIENTE
                    }
                }
            }
        }
    }
)
async def enviar_solicitud_individual_endpoint(
    us_codigo: Annotated[int, Body(embed=True)],
    gr_codigo: Annotated[int, Body(embed=True)],
    servicio: Annotated[GrupoRetornoServicio, Depends(obtener_grupo_retorno_servicio)]
):
    """
    Endpoint para que un líder solicite la incorporación de un individuo a un grupo.
    """
    solicitud = await servicio.crear_solicitud_grupo_retorno(us_codigo, gr_codigo)
    return solicitud

@grupo_retorno_router.post(
    "/registro",
    response_model=RegistroRetornoGrupoRespuesta,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar un grupo en un retorno",
    description="Asocia un grupo completo a un retorno vigente, validando que tenga integrantes adicionales al líder."
)
async def registrar_grupo_en_retorno_endpoint(
    datos: RegistroRetornoGrupoCrear,
    servicio: Annotated[RegistroRetornoGrupoServicio, Depends(obtener_registro_retorno_grupo_servicio)]
):
    """
    Endpoint para registrar la participación de un grupo en el evento de retorno.
    """
    return await servicio.crear_registro_retorno_grupo(datos)

@grupo_retorno_router.get(
    "/{gr_codigo}/miembros",
    response_model=List[UsuarioSalida],
    summary="Ver usuarios pertenecientes a un grupo",
    description="Lista todos los usuarios que han aceptado unirse y forman parte activa de un grupo de retorno."
)
async def obtener_miembros_grupo_endpoint(
    gr_codigo: int,
    servicio: Annotated[RegistroRetornoGrupoServicio, Depends(obtener_registro_retorno_grupo_servicio)]
):
    """
    Endpoint para obtener la lista de integrantes de un grupo.
    """
    return await servicio.obtener_usuarios_por_grupo(gr_codigo)
@grupo_retorno_router.patch("/solicitudes/aceptar/{solicitud_id}", 
              response_model= SolicitudRetornoGrupoRespuesta,
              status_code= status.HTTP_200_OK,
              summary="Aceptar solicitud de grupo de retorno", 
              description="Acepta una solicitud pendiente para unirse a un grupo de retorno específico. " \
              "Cambia el estado de la solicitud a aceptada y agrega al usuario al grupo.")
async def aceptar_solicitud_grupo_retorno(solicitud_id: int, servicio: GrupoRetornoServicio = Depends(obtener_grupo_retorno_servicio)):
    return await servicio.aceptar_solicitud_grupo_retorno(solicitud_id)

@grupo_retorno_router.patch("/solicitudes/rechazar/{solicitud_id}", 
              response_model= SolicitudRetornoGrupoRespuesta,
              status_code= status.HTTP_200_OK,
              summary="Rechazar solicitud de grupo de retorno", 
              description="Rechaza una solicitud pendiente para unirse a un grupo de retorno específico. " \
              "Cambia el estado de la solicitud a rechazada.")
async def rechazar_solicitud_grupo_retorno(solicitud_id: int, servicio: GrupoRetornoServicio = Depends(obtener_grupo_retorno_servicio)):
    return await servicio.rechazar_solicitud_grupo_retorno(solicitud_id)

@grupo_retorno_router.get("/solicitudes/recientes/usuario/{usuario_id}",
            response_model=list[SolicitudRetornoGrupoUsuarioRespuesta],
            status_code=status.HTTP_200_OK,
            summary="Obtener solicitudes de grupos de retorno por usuario",
            description="Obtiene las solicitudes de ingreso a grupos de retorno recientes (ultimos 30 días) dirigidas a un usuario específico, ordenadas por fecha de creación más reciente primero.")
async def obtener_solicitudes_recientes_grupo_por_usuario(usuario_id: int, servicio: GrupoRetornoServicio = Depends(obtener_grupo_retorno_servicio)):
    return await servicio.obtener_solicitudes_recientes_por_usuario(usuario_id)

@grupo_retorno_router.get("/solicitudes/grupo/{grupo_retorno_id}",
            response_model=list[SolicitudRetornoGrupoLiderRespuesta],
            status_code=status.HTTP_200_OK,
            summary="Obtener solicitudes de grupos de retorno por grupo de retorno",
            description="Obtiene las solicitudes de ingreso a grupos de retorno enviadas por el lider del grupo.")
async def obtener_solicitudes_grupo_por_lider(grupo_retorno_id: int, servicio: GrupoRetornoServicio = Depends(obtener_grupo_retorno_servicio)):
    return await servicio.obtener_solicitudes_por_grupo_retorno(grupo_retorno_id)

    
