"""
Módulo que define los endpoints HTTP para la entidad Colonia.
Expone las rutas de la API relacionadas con la gesti+on de colonias
colombianas, conectando las solicitudes HTTP con la capa de servicios
y documentando cada endpoint en Swagger.
"""
from app.colonias.repositories.colonia_repository import ColoniaRepository
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.colonias.schemas.colonia_schemas import ColoniaCrear, ColoniaRespuesta, ColoniaEstablecerLider
from app.colonias.services.colonia_services import ColoniaService

def get_colonia_service(db: Session = Depends(get_db)) -> ColoniaService:
    """Dependencia para obtener una instancia de ColoniaService con el repositorio inyectado."""
    repositorio = ColoniaRepository(db)
    return ColoniaService(repositorio)

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
def crear_colonia(datos: ColoniaCrear, servicio: ColoniaService = Depends(get_colonia_service)):
    """Endpoint para crear una nueva colonia"""
    return servicio.servicio_crear_colonia(datos)

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
def asignar_lider(colonia_codigo: int, datos: ColoniaEstablecerLider, servicio: ColoniaService = Depends(get_colonia_service)):
    """Endpoint para asignar un líder a una colonia existente"""
    return servicio.servicio_establecer_lider(colonia_codigo, datos.lider_id)