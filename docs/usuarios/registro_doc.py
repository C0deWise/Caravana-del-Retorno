from fastapi import Body
from typing import Annotated
from app.usuarios.schemas.usuario_esquemas import UsuarioSchema


registrar_docs = dict(
    summary="Registrar un nuevo usuario",
    description="""
Crea un nuevo usuario en el sistema.

**Acceso:** Público, no requiere autenticación.

**Restricciones por campo:**
- `us_tipo_doc`: Debe ser `CC` o `CE`.
- `us_documento`: No puede estar vacío.
- `us_correo`: Debe tener formato válido (usuario@dominio.com).
- `us_celular`: Solo dígitos, espacios y `+`, entre 7 y 15 dígitos.
- `us_contrasenia`: Mínimo 8 caracteres, máximo 72 bytes.
- `us_nombre` y `us_apellido`: Solo letras.
- `us_genero`: Debe ser `F`, `M` u `otro`.
- `us_fecha_nacimiento`: Formato `YYYY-MM-DD`.
- `co_codigo`: Opcional, FK hacia la tabla colonia.
- `ro_codigo`: Opcional, por defecto `1` (usuario).
    """,
    responses={
        201: {
            "description": "Usuario registrado exitosamente.",
            "content": {
                "application/json": {
                    "example": {"mensaje": "Usuario registrado exitosamente.", "id": 1}
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
    UsuarioSchema,
    Body(
        openapi_examples={
            "ejemplo_basico": {
                "summary": "Registro básico",
                "value": {
                    "us_tipo_doc": "CC",
                    "us_documento": "1234567890",
                    "us_celular": "+57 300 123 4567",
                    "us_correo": "juan.perez@gmail.com",
                    "us_contrasenia": "MiContrasenia123",
                    "us_nombre": "Juan",
                    "us_apellido": "Perez",
                    "us_genero": "M",
                    "us_fecha_nacimiento": "1995-06-15",
                    "us_pais": "Colombia",
                },
            },
            "ejemplo_completo": {
                "summary": "Registro completo",
                "value": {
                    "us_tipo_doc": "CE",
                    "us_documento": "9876543210",
                    "us_celular": "+57 315 987 6543",
                    "us_correo": "maria.lopez@empresa.co",
                    "us_contrasenia": "OtraContrasenia456",
                    "co_codigo": 1,
                    "ro_codigo": 2,
                    "us_nombre": "Maria",
                    "us_apellido": "Lopez",
                    "us_genero": "F",
                    "us_fecha_nacimiento": "1990-03-22",
                    "us_pais": "Colombia",
                    "us_departamento": "Cauca",
                    "us_ciudad": "Popayan",
                },
            },
        }
    ),
]