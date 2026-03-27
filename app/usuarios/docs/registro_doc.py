"""
    registro_doc.py contiene la documentación para el endpoint de registro de usuarios.
    Aquí se definen los resúmenes, descripciones, ejemplos y respuestas.
"""

from fastapi import Body
from typing import Annotated
from app.usuarios.schemas.usuario_esquemas import UsuarioCrear


registrar_docs = dict(
    summary="Registrar un nuevo usuario",
    description="""
Crea un nuevo usuario en el sistema.

**Acceso:** Público, no requiere autenticación.

**Restricciones por campo:**
- `tipo_doc`: Debe ser `CC` o `CE`.
- `documento`: No puede estar vacío.
- `correo`: Debe tener formato válido (usuario@dominio.com).
- `celular`: Solo dígitos, espacios y `+`, entre 7 y 15 dígitos.
- `contrasenia`: Mínimo 8 caracteres, máximo 72 bytes.
- `nombre` y `apellido`: Solo letras.
- `genero`: Debe ser `F`, `M` u `otro`.
- `fecha_nacimiento`: Formato `YYYY-MM-DD`.
- `codigo_colonia`: Opcional, FK hacia la tabla colonia.
- `codigo_rol`: Opcional, por defecto `1` (usuario).
    """,
    responses={
        201: {
            "description": "Usuario registrado exitosamente.",
            "content": {
                "application/json": {
                    "example": {"mensaje": "Usuario registrado exitosamente.", "nombre": "Nombre Completo"}
                }
            },
        },
        400: {
            "description": "Error de validación o violación de integridad.",
            "content": {
                "application/json": {
                    "examples": {
                        "documento_duplicado": {
                            "summary": "Documento duplicado",
                            "value": {"detail": "El documento ya se encuentra registrado."},
                        },
                        "correo_duplicado": {
                            "summary": "Correo duplicado",
                            "value": {"detail": "El correo ya se encuentra registrado."},
                        },
                        "celular_duplicado": {
                            "summary": "Celular duplicado",
                            "value": {"detail": "El celular ya se encuentra registrado."},
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


registrar_body = Annotated[
    UsuarioCrear,
    Body(
        openapi_examples={
            "ejemplo_basico": {
                "summary": "Registro básico",
                "value": {
                    "tipo_doc": "CC",
                    "documento": "1234567890",
                    "celular": "+57 300 123 4567",
                    "correo": "juan.perez@gmail.com",
                    "contrasenia": "MiContrasenia123",
                    "nombre": "Juan",
                    "apellido": "Perez",
                    "genero": "M",
                    "fecha_nacimiento": "1995-06-15",
                    "pais": "Colombia",
                },
            },
            "ejemplo_completo": {
                "summary": "Registro completo",
                "value": {
                    "tipo_doc": "CE",
                    "documento": "9876543210",
                    "celular": "+57 315 987 6543",
                    "correo": "maria.lopez@empresa.co",
                    "contrasenia": "OtraContrasenia456",
                    "codigo_colonia": 1,
                    "codigo_rol": 2,
                    "nombre": "Maria",
                    "apellido": "Lopez",
                    "genero": "F",
                    "fecha_nacimiento": "1990-03-22",
                    "pais": "Colombia",
                    "departamento": "Cauca",
                    "ciudad": "Popayan",
                },
            },
        }
    ),
]