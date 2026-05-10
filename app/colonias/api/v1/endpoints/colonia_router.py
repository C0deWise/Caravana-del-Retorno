"""
    colonia_router.py - Endpoints relacionados con colonias y solicitudes de colonias.
    Módulo que define los endpoints HTTP para la entidad Colonia.
    Expone las rutas de la API relacionadas con la gesti+on de colonias
    colombianas, conectando las solicitudes HTTP con la capa de servicios
    y documentando cada endpoint en Swagger.  
"""

from fastapi import APIRouter, Depends, status, Response
from typing import Union
from app.colonias.models.colonia_model import ColoniaEstado
from app.usuarios.repository.usuario_repositorio import UsuarioRepositorio
from app.usuarios.schemas.usuario_esquemas import UsuarioConsultaColonia
from sqlalchemy.ext.asyncio import AsyncSession
from app.colonias.excepciones.excepciones import ColoniaInactiva, ColoniaNoEncontrada, UsuarioNoEncontrado
from typing import Annotated
from app.colonias.services.colonia_services import ColoniaService
from sqlalchemy.orm import Session
from app.colonias.repositories.solicitud_colonia_repository import SolicitudColoniaRepository
from app.colonias.repositories.colonia_repository import ColoniaRepository
from app.core.database import get_db
from app.usuarios.api.v1.usuario_router import get_usuario_servicio
from app.colonias.schemas.colonia_schemas import ColoniaCrear, ColoniaRespuesta, ColoniaEstablecerLider, ColoniaSacarMiembro, UsuarioRemovidoColoniaRespuesta
from app.colonias.schemas.colonia_solicitud_schemas import SolicitudColoniaCrear, SolicitudColoniaRespuesta, MiembroRegistradoColoniaRespuesta
from app.colonias.services.colonia_services import ColoniaService
from app.colonias.services.solicitud_colonias_services import SolicitudColoniaService
from app.usuarios.services.usuario_servicio import UsuarioServicio
from app.retornos.repositorios.retorno_repositorio import RetornoRepository
from app.retornos.repositorios.registro_retorno_repositorio import RegistroRetornoRepositorio
from app.retornos.servicios.registro_retorno_servicio import RegistroRetornoServicio
from app.colonias.docs.docs_colonia import desactivar_colonia_docs, cambiar_lider_colonia_docs, sacar_miembro_colonia_docs, obtener_colonias_activas_docs,  crear_colonia_body
from json import dumps

from app.colonias.docs.docs_solicitud_colonia import (
    crear_solicitud_docs,
    obtener_solicitudes_pendientes_docs,
    obtener_solicitudes_recientes_colonia_docs,
    obtener_solicitudes_recientes_usuario_docs,
)

def get_solicitud_colonia_servicio(db: Annotated[AsyncSession, Depends(get_db)]) -> SolicitudColoniaRepository:
    repositorio = SolicitudColoniaRepository(db)
    return SolicitudColoniaService(repositorio)


def get_colonia_service(db: Annotated[AsyncSession, Depends(get_db)]) -> ColoniaService:
    """Dependencia para obtener una instancia de ColoniaService con el repositorio inyectado."""
    repositorio = ColoniaRepository(db)
    servicio_usuario = UsuarioServicio(UsuarioRepositorio(db))
    servicio_registro_retorno = RegistroRetornoServicio(RegistroRetornoRepositorio(db), RetornoRepository(db), servicio_usuario)
    return ColoniaService(repositorio, servicio_usuario, servicio_registro_retorno)

router = APIRouter()

@router.post(
    "/",
    response_model = ColoniaRespuesta,
    status_code = status.HTTP_201_CREATED,
    summary = "Crear una colonia",
    description = """
    Crea una nueva colonia colombiana en el sistema.

    **Campos requeridos:**
    - **pais** (str, obligatorio): País donde se encuentra la colonia. Solo letras, tildes y espacios. Ejemplo: `Colombia`.
    - **departamento** (str, obligatorio): Departamento o estado. Solo letras, tildes y espacios. Ejemplo: `Cauca`.
    - **ciudad** (str, obligatorio): Ciudad de la colonia. Solo letras, tildes y espacios. Ejemplo: `Popayán`.

    **Restricciones:**
    - Todos los campos son obligatorios.
    - Solo se permiten caracteres alfabéticos, tildes, espacios y guiones.
    - No se permite crear dos colonias con el mismo país, departamento y ciudad.

    **Autenticación:** Este endpoint no requiere autenticación.
    """,
    responses = {
        201: {
            "description": "Colonia creada exitosamente.",
            "model": ColoniaRespuesta
        },
        409: {
            "description": "Ya existe una colonia con la misma ubicación.",
            "content": {

            }
        },
        422: {
            "description": "Datos inválidos o campos faltantes.",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "El campo solo puede contener letras."
                    }
                }
            },
        }
    }
)
async def crear_colonia(datos: crear_colonia_body, servicio: Annotated[ColoniaService, Depends(get_colonia_service)]):
    """Endpoint para crear una nueva colonia"""
    return await servicio.servicio_crear_colonia(datos)


@router.patch(
    "/solicitud-colonia/{codigo}/aceptar",
    response_model = SolicitudColoniaRespuesta,
    status_code = status.HTTP_200_OK,
    summary = "Aceptar una solicitud de ingreso a una colonia",
    description = "Acepta una solicitud pendiente, cambiando su estado a 'aceptada'.",
    responses = {
        200: {
            "description": "Solicitud aceptada exitosamente.",
            "model": SolicitudColoniaRespuesta
        },
        404: {
            "description": "Solicitud no encontrada.",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Solicitud con código 123 no encontrada."
                    }
                }
            }
        },
        409: {
            "description": "Solicitud en estado no válido para aceptar.",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Solo se pueden aceptar solicitudes pendientes. Solicitud 123 está en estado expirada."
                    }
                }
            }
        }
    }
)
async def aceptar_solicitud_colonia(codigo: int, servicio: Annotated[SolicitudColoniaService, Depends(get_solicitud_colonia_servicio)]):
    return await servicio.aceptar_solicitud(codigo)

@router.patch(
    "/solicitud-colonia/{codigo}/rechazar",
    response_model = SolicitudColoniaRespuesta,
    status_code = status.HTTP_200_OK,
    summary = "Rechaza una solicitud de ingreso a una colonia",
    description = "Rechaza una solicitud pendiente, cambiando su estado a 'rechazada'.",
    responses = {
        200: {
            "description": "Solicitud rechazada exitosamente.",
            "model": SolicitudColoniaRespuesta
        },
        404: {
            "description": "Solicitud no encontrada.",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Solicitud con código 123 no encontrada."
                    }
                }
            }
        },
        409: {
            "description": "Solicitud en estado no válido para rechazar.",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Solo se pueden rechzar solicitudes pendientes. Solicitud 123 está en estado expirada."
                    }
                }
            }
        }
    }
)
async def rechazar_solicitud_colonia(codigo: int, servicio: Annotated[SolicitudColoniaService, Depends(get_solicitud_colonia_servicio)]):
    return await servicio.rechazar_solicitud(codigo)

@router.get(
    "/",
    response_model = list[ColoniaRespuesta],
    status_code = status.HTTP_200_OK,
    summary = "Obtener todas las colonias",
    description = "Obtiene una lista de todas las colonias registradas en el sistema",
)
async def obtener_colonias(servicio: Annotated[ColoniaService, Depends(get_colonia_service)]):
    return await servicio.obtener_colonias()

@router.get(
    "/{colonia_codigo}",
    response_model = ColoniaRespuesta,
    status_code = status.HTTP_200_OK,
    summary = "Obtener información de una colonia",
    description = "Obtiene la información detallada de una colonia específica por su código",
)
async def obtener_colonia(colonia_codigo: int, servicio: ColoniaService = Depends(get_colonia_service)):
    return await servicio.obtener_colonia(colonia_codigo)

@router.post(
    "/crear-solicitud",
    response_model=Union[SolicitudColoniaRespuesta, MiembroRegistradoColoniaRespuesta], **crear_solicitud_docs
)
async def crear_solicitud_colonia(
    datos: SolicitudColoniaCrear,
    servicio_usuario: UsuarioServicio = Depends(get_usuario_servicio),
    servicio: SolicitudColoniaService = Depends(get_solicitud_colonia_servicio),
    servicio_colonia: ColoniaService = Depends(get_colonia_service)
):
    
    if not await servicio_usuario.existe_usuario("us_codigo", datos.codigo_usuario):
        raise UsuarioNoEncontrado(datos.codigo_usuario)
    colonia = await servicio_colonia.obtener_colonia(datos.codigo_colonia)
    if not colonia:
        raise ColoniaNoEncontrada(datos.codigo_colonia)
    if colonia.estado == ColoniaEstado.INACTIVA:
        raise ColoniaInactiva(datos.codigo_colonia)
    
        
    resultado = await servicio.crear_solicitud(datos)
    
    if isinstance(resultado, MiembroRegistradoColoniaRespuesta):
        return Response(
            content=resultado.model_dump_json(),
            status_code=status.HTTP_200_OK,
            media_type="application/json"
        )
    
    return resultado


@router.get(
    "/solicitudes-pendientes/{cod_colonia}",
    response_model=list[SolicitudColoniaRespuesta], **obtener_solicitudes_pendientes_docs
)
async def obtener_solicitudes_pendientes_colonia(
    cod_colonia: int,
    servicio: Annotated[SolicitudColoniaService, Depends(get_solicitud_colonia_servicio)],
):
    return await servicio.obtener_solicitudes_pendientes_colonia(cod_colonia)


@router.get(
    "/solicitudes-recientes/{cod_colonia}",
    response_model=list[SolicitudColoniaRespuesta], **obtener_solicitudes_recientes_colonia_docs
)
async def obtener_solicitudes_recientes_colonia(
    cod_colonia: int,
    servicio: Annotated[SolicitudColoniaService, Depends(get_solicitud_colonia_servicio)],
):
    return await servicio.obtener_solicitudes_recientes_colonia(cod_colonia)


@router.get(
    "/solicitudes-recientes-usuario/{cod_usuario}",
    response_model=list[SolicitudColoniaRespuesta], **obtener_solicitudes_recientes_usuario_docs
)
async def obtener_solicitudes_recientes_usuario(
    cod_usuario: int,
    servicio: Annotated[SolicitudColoniaService, Depends(get_solicitud_colonia_servicio)],
):
    return await servicio.obtener_solicitudes_recientes_usuario(cod_usuario)
    

@router.patch(
    "/establecer_lider/{colonia_codigo}/",
    response_model = ColoniaRespuesta,
    status_code = status.HTTP_200_OK,
    summary = "Asignar líder a una colonia",
    description = """
    Asigna un líder a una colonia existente.

    **Parámetros de ruta:**
    - **colonia_codigo** (int, obligatorio): Código único de la colonia a la que se le asignará el líder.
    - **lider_id** (int, obligatorio): ID del líder que se asignará a la colonia.

    **Restricciones:**
    - La colonia debe existir en la base de datos.
    - El líder debe existir en la base de datos.

    **Autenticación:** Este endpoint no requiere autenticación.
    """,
    responses = {
        200: {
            "description": "Líder asignado exitosamente.",
            "model": ColoniaRespuesta
        },
        404: {
            "description": "Colonia o líder no encontrado.",
            "content": {

            }
        },
        422: {
            "description": "Datos inválidos o campos faltantes.",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Colonia con código 123 no encontrada."
                    }
                }
            },
        }
    }
)
async def asignar_lider(colonia_codigo: int, datos: ColoniaEstablecerLider, servicio: Annotated[ColoniaService, Depends(get_colonia_service)]) -> ColoniaRespuesta:
    """Endpoint para asignar un líder a una colonia existente"""
    return await servicio.servicio_establecer_lider(colonia_codigo, datos.lider)

@router.patch(
    "/desactivar/{colonia_codigo}/",
    response_model=ColoniaRespuesta, **desactivar_colonia_docs
)
async def desactivar_colonia(
    colonia_codigo: int,
    servicio: ColoniaService = Depends(get_colonia_service)
) -> ColoniaRespuesta:
    """Endpoint para desactivar una colonia existente"""
    return await servicio.desactivar_colonia(colonia_codigo)

@router.get(
    "/colonias-activas/",
    response_model=list[ColoniaRespuesta], **obtener_colonias_activas_docs
)
async def obtener_colonias_activas(servicio: ColoniaService = Depends(get_colonia_service)) -> list[ColoniaRespuesta]:
    """Endpoint para obtener la lista de colonias activas"""
    return await servicio.obtener_colonias_activas()
@router.patch(
    "/cambiar-lider/{colonia_codigo}/",
    response_model=ColoniaRespuesta, **cambiar_lider_colonia_docs
)
async def cambiar_lider_colonia(
    colonia_codigo: int,
    datos: ColoniaEstablecerLider,
    servicio: ColoniaService = Depends(get_colonia_service)
) -> ColoniaRespuesta:
    """Endpoint para cambiar el líder de una colonia existente"""
    return await servicio.cambiar_lider_colonia(colonia_codigo, datos.lider)

@router.patch(
    "/sacar-miembro/{colonia_codigo}/",
    response_model=UsuarioRemovidoColoniaRespuesta,
    **sacar_miembro_colonia_docs
)
async def sacar_miembro_colonia(
    colonia_codigo: int,
    datos: ColoniaSacarMiembro,
    servicio: ColoniaService = Depends(get_colonia_service)
) -> UsuarioRemovidoColoniaRespuesta:
    """Endpoint para sacar un miembro de una colonia existente"""
    return await servicio.remover_miembro_colonia(colonia_codigo, datos.miembro_id)
