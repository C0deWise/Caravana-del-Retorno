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
from app.colonias.services.colonia_services import servicio_crear_colonia

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