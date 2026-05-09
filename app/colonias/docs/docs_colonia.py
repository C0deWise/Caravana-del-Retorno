"""
Documentación para la función de desactivación de una colonia.
"""

from fastapi import status, Body
from typing import Annotated

from app.colonias.schemas.colonia_schemas import ColoniaCrear

desactivar_colonia_docs = dict(
    status_code=status.HTTP_200_OK,
    summary="Desactivar una colonia",
    description="""
    Desactiva una colonia existente por su código.
    
    Si la colonia tiene usuarios asociados:
    - Los usuarios serán desasociados de la colonia
    - Si algún usuario es líder, su rol será cambiado a usuario regular
    
    La colonia será marcada como inactiva y no aparecerá en listados públicos.
    """,
    responses={
        200:{
            "description": "Colonia desactivada exitosamente.",
            "content": {
                "application/json": {
                    "example": {
                        "codigo": 1,
                        "pais": "Colombia",
                        "departamento": "Antioquia",
                        "ciudad": "Medellín",
                        "estado": "inactiva",
                        "lider": None
                    }
                }
            }
        },
        404: {
            "description": "Colonia no encontrada.",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Colonia con código 999 no encontrada"
                    }
                }
            }
        },
        409: {
            "description": "La colonia ya está desactivada.",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "La colonia con código 1 ya está desactivada"
                    }
                }
            }
        }
    }
)

cambiar_lider_colonia_docs = dict(
    status_code=status.HTTP_200_OK,
    summary="Cambiar líder de una colonia",
    description="""
    Cambia el líder asignado a una colonia existente.

    Requiere el código de la colonia (path) y el ID del nuevo líder (body).

    Reglas:
    - El usuario (nuevo líder) debe existir.
    - El usuario debe ser miembro de la colonia (`co_codigo == colonia_codigo`).
    - La colonia debe tener un líder actualmente asignado.
    - El nuevo líder no puede ser el mismo líder actual.

    Efectos:
    - Se revoca el rol de líder al usuario anterior.
    - Se asigna el rol de líder al nuevo usuario.
    - Se actualiza `colonia.lider` con el nuevo ID.
    """,
    responses={
        200: {
            "description": "El líder de la colonia ha sido actualizado exitosamente.",
            "content": {
                "application/json": {
                    "example": {
                        "codigo": 1,
                        "pais": "Colombia",
                        "departamento": "Antioquia",
                        "ciudad": "Medellín",
                        "estado": "activa",
                        "lider": 2
                    }
                }
            },
        },
        404: {
            "description": "Colonia o usuario no encontrado.",
            "content": {
                "application/json": {
                    "examples": {
                        "colonia_no_encontrada": {
                            "summary": "Colonia no encontrada",
                            "value": {"detail": "Colonia con ID 999 no encontrada."}
                        },
                        "usuario_no_encontrado": {
                            "summary": "Usuario no encontrado",
                            "value": {"detail": "Usuario con ID 999 no encontrado."}
                        }
                    }
                }
            },
        },
        409: {
            "description": "Conflicto de negocio (colonia sin líder, usuario ya es líder o usuario no es miembro).",
            "content": {
                "application/json": {
                    "examples": {
                        "colonia_sin_lider": {
                            "summary": "La colonia no tiene líder",
                            "value": {"detail": "La colonia con ID 1 no tiene un líder asignado."}
                        },
                        "usuario_ya_es_lider": {
                            "summary": "El usuario ya es el líder actual",
                            "value": {"detail": "El usuario con ID 2 ya es líder actual de la colonia con ID 1."}
                        },
                        "usuario_no_es_miembro": {
                            "summary": "Usuario no pertenece a la colonia",
                            "value": {"detail": "El usuario con ID 2 no es miembro de la colonia con ID 1."}
                        },
                    }
                }
            },
        },
        422: {
            "description": "Body inválido (por ejemplo, no se envió el campo `lider`).",
            "content": {
                "application/json": {
                    "example": {
                        "detail": [
                            {
                                "loc": ["body", "lider"],
                                "msg": "Field required",
                                "type": "missing"
                            }
                        ]
                    }
                }
            },
        },
    },
)

crear_colonia_body = Annotated[
    ColoniaCrear,
    Body(
        openapi_examples={
            "ejemplo_colombia": {
                "summary": "Colonia en Colombia",
                "value": {
                    "pais": "Colombia",
                    "departamento": "Cauca",
                    "ciudad": "Popayán",
                    "lider": None
                }
            },
            "ejemplo_extranjera": {
                "summary": "Colonia extranjera",
                "value": {
                    "pais": "Argentina",
                    "lider": None
                }
            },
            "ejemplo_con_lider": {
                "summary": "Colonia con líder asignado",
                "value": {
                    "pais": "Colombia",
                    "departamento": "Cundinamarca",
                    "ciudad": "Bogotá",
                    "lider": 2
                }
            },
        }
    )
]