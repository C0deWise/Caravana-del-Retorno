"""
Módulo que define los endpoints HTTP para la entidad Colonia.
Expone las rutas de la API relacionadas con la gesti+on de colonias
colombianas, conectando las solicitudes HTTP con la capa de servicios
y documentando cada endpoint en Swagger.
"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.colonias.schemas.colonia_schemas import ColoniaCrear, ColoniaRespuesta
from app.colonias.schemas.colonia_solicitud_schemas import SolicitudColoniaCrear, SolicitudColoniaResponse
from app.colonias.services.colonia_services import servicio_crear_colonia
from app.colonias.services.solicitud_colonia_services import SolicitudColoniaService
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
def crear_colonia(datos: ColoniaCrear, db: Session = Depends(get_db)):
    """Endpoint para crear una nueva colonia"""
    return servicio_crear_colonia(db, datos)

@router.post(
    "/solicitud-colonia/",
    response_model = SolicitudColoniaResponse,
    status_code = status.HTTP_201_CREATED,
    summary = "Crear una solicitud de ingreso a una colonia",
    description = "Crea una nueva solicitud de ingreso a una colonia con el código de usuario y el código de colonia",
)
def crear_solicitud_colonia(datos: SolicitudColoniaCrear, db: Session = Depends(get_db)):
    return SolicitudColoniaService().crear_solicitud(db, datos)

@router.patch(
    "/solicitud-colonia/{codigo}/aceptar",
    response_model = SolicitudColoniaResponse,
    status_code = status.HTTP_200_OK,
    summary = "Aceptar una solicitud de ingreso a una colonia",
    description = "Acepta una solicitud pendiente, cambiando su estado a 'aceptada'.",
    responses = {
        200: {
            "description": "Solicitud aceptada exitosamente.",
            "model": SolicitudColoniaResponse
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
def aceptar_solicitud_colonia(codigo: int, db: Session = Depends(get_db)):
    return SolicitudColoniaService().aceptar_solicitud(db, codigo)

@router.patch(
    "/solicitud-colonia/{codigo}/rechazar",
    response_model = SolicitudColoniaResponse,
    status_code = status.HTTP_200_OK,
    summary = "Rechaza una solicitud de ingreso a una colonia",
    description = "Rechaza una solicitud pendiente, cambiando su estado a 'rechazada'.",
    responses = {
        200: {
            "description": "Solicitud rechazada exitosamente.",
            "model": SolicitudColoniaResponse
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
def rechazar_solicitud_colonia(codigo: int, db: Session = Depends(get_db)):
    return SolicitudColoniaService().rechazar_solicitud(db, codigo)

