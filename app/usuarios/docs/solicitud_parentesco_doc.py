"""
    solicitud_parentesco_doc.py contiene la documentación para el endpoint de solicitud de parentesco.
    Aquí se definen los resúmenes, descripciones, ejemplos y respuestas.
"""

from fastapi import Body
from typing import Annotated
from app.usuarios.schemas.parentesco_esquemas import ParentescoCrear


solicitar_parentesco_docs = dict(
    summary="Solicitar parentesco entre usuarios",
    description="""
Crea una solicitud de parentesco entre dos usuarios del sistema.

**Acceso:** Privado, requiere autenticación.

**Restricciones por campo:**
- `codigo_solicitante`: Debe corresponder a un usuario existente en el sistema.
- `codigo_destinatario`: Debe corresponder a un usuario existente en el sistema. No puede ser igual a `codigo_solicitante`.
- `tipo_parentesco`: Debe ser uno de los valores permitidos por el enum `tipoParentesco` (ej. `padre`, `madre`, `hijo`, `hermano`, etc.).
    """,
    responses={
        201: {
            "description": "Solicitud de parentesco creada exitosamente.",
            "content": {
                "application/json": {
                    "example": {
                        "mensaje": "Solicitud de parentesco enviada exitosamente.",
                        "codigo_solicitante": 1,
                        "codigo_destinatario": 2,
                        "tipo_parentesco": "hermano (a)",
                    }
                }
            },
        },
        400: {
            "description": "Error de validación o violación de integridad.",
            "content": {
                "application/json": {
                    "examples": {
                        "solicitud_duplicada": {
                            "summary": "Solicitud duplicada",
                            "value": {"detail": "Ya existe una solicitud de parentesco entre estos usuarios."},
                        },
                        "mismo_usuario": {
                            "summary": "Solicitante igual al destinatario",
                            "value": {"detail": "El solicitante y el destinatario no pueden ser el mismo usuario."},
                        },
                        "usuario_no_encontrado": {
                            "summary": "Usuario no encontrado",
                            "value": {"detail": "El usuario destinatario no existe en el sistema."},
                        },
                    }
                }
            },
        },
        422: {
            "description": "Error de validación de campos.",
        },
    },
)


solicitar_parentesco_body = Annotated[
    ParentescoCrear,
    Body(
        openapi_examples={
            "ejemplo_basico": {
                "summary": "Solicitud básica",
                "value": {
                    "codigo_solicitante": 1,
                    "codigo_destinatario": 2,
                    "tipo_parentesco": "hermano (a)",
                },
            },
            "ejemplo_completo": {
                "summary": "Solicitud con tipo de parentesco distinto",
                "value": {
                    "codigo_solicitante": 5,
                    "codigo_destinatario": 12,
                    "tipo_parentesco": "padre",
                },
            },
        }
    ),
]