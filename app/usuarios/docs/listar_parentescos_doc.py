"""
Documentación para la operación de listar parentescos de un usuario.
Este módulo define la documentación para el endpoint que permite obtener una lista de todas 
las relaciones de parentesco asociadas a un usuario específico, ya sea como solicitante o destinatario. 
Se incluyen detalles sobre el acceso, los parámetros requeridos y las posibles respuestas del endpoint.
"""

from app.usuarios.schemas.parentesco_esquemas import ParentescoRespuestaDetallada
from fastapi import Body
from typing import Annotated

listar_parentescos_docs = dict(
    summary="Listar parentescos de un usuario",
    description="""
Obtiene una lista de todas 
las relaciones de parentesco asociadas a un usuario específico, ya sea como solicitante o destinatario.
**Acceso:** Privado, requiere autenticación.
**Parámetros:**
- `codigo_usuario`: El código único del usuario para el cual se desean listar los parentescos. Debe ser un entero positivo que corresponda a un usuario existente en el sistema.
    """,
    responses={
        200: {
            "description": "Lista de parentescos obtenida exitosamente.",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "codigo_parentesco": 1,
                            "codigo_solicitante": 1,
                            "codigo_destinatario": 2,
                            "tipo_parentesco": "hermano (a)",
                            "estado": "aceptada"
                        },
                        {
                            "codigo_parentesco": 2,
                            "codigo_solicitante": 3,
                            "codigo_destinatario": 1,
                            "tipo_parentesco": "padre",
                            "estado": "pendiente"
                        }
                    ]
                }
            },
        },
        400: {
            "description": "Error de validación o usuario no encontrado.",
            "content": {
                "application/json": {
                    "examples": {
                        "usuario_no_encontrado": {
                            "summary": "Usuario no encontrado",
                            "value": {"detail": "El usuario no existe en el sistema."},
                        },
                    }
                }
            },
        },
    },
)