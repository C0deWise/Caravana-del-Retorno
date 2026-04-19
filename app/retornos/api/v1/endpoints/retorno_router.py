"""
Endpoints HTTP para el módulo Retorno.
Expone operaciones de creación y consulta bajo el prefijo /retornos,
con documentación Swagger integrada.
"""

from app.retornos.esquemas.registro_retorno_esquema import RegistroRetornoCrear, RegistroRetornoRespuesta
from app.retornos.repositorios.registro_retorno_repositorio import RegistroRetornoRepositorio
from app.retornos.repositorios.retorno_repositorio import RetornoRepository
from app.retornos.servicios.registro_retorno_servicio import RegistroRetornoServicio
from app.usuarios.repository.usuario_repositorio import UsuarioRepositorio
from app.usuarios.services.usuario_servicio import UsuarioServicio
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.retornos.esquemas.retorno_esquemas import RetornoCreate, RetornoResponse
from app.retornos.servicios.retorno_servicio import RetornoService

router = APIRouter(
    prefix="/retornos",
    tags=["Retornos"],
)

def obtener_registro_retorno_servicio(db: AsyncSession = Depends(get_db)) -> RegistroRetornoServicio:
    repositorio = RegistroRetornoRepositorio(db)
    retorno_repositorio = RetornoRepository(db)
    usuario_servicio = UsuarioServicio(UsuarioRepositorio(db), None)
    
    return RegistroRetornoServicio(
        repositorio,
        retorno_repositorio,
        usuario_servicio
    )


def obtener_retorno_servicio(db: AsyncSession = Depends(get_db)) -> RetornoService:
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
async def crear_retorno(data: RetornoCreate, servicio: RetornoService = Depends(obtener_retorno_servicio)):
    return await servicio.crear_retorno(data)


@router.get(
    "/",
    response_model=list[RetornoResponse],
    summary="Listar todos los retornos",
    description="Obtiene el listado completo de retornos registrados en el sistema.",
)
async def listar_retornos(servicio: RetornoService = Depends(obtener_retorno_servicio)):
    return await servicio.listar_retornos()


@router.get(
    "/{codigo}",
    response_model=RetornoResponse,
    summary="Obtener retorno por código",
    description="Busca y retorna un retorno específico usando su código primario. Retorna 404 si no existe.",
)
async def obtener_retorno(codigo: int, servicio: RetornoService = Depends(obtener_retorno_servicio)):
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
async def inscribir_usuario_en_retorno(registro: RegistroRetornoCrear, servicio: RegistroRetornoServicio = Depends(obtener_registro_retorno_servicio)):
    return await servicio.crear_registro_retorno(registro)