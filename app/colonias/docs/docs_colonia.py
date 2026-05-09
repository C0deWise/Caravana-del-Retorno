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

obtener_colonias_activas_docs = dict(
    summary="Obtener colonias activas",
    description="Obtiene una lista de todas las colonias que están actualmente activas.",
    status_code=status.HTTP_200_OK,
    responses={
        200: {
            "description": "Lista de colonias activas obtenida exitosamente.",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "codigo": 1,
                            "pais": "Colombia",
                            "departamento": "Antioquia",
                            "ciudad": "Medellín",
                            "estado": "activa",
                            "lider": 10
                        },
                        {
                            "codigo": 2,
                            "pais": "Colombia",
                            "departamento": "Cundinamarca",
                            "ciudad": "Bogotá",
                            "estado": "activa",
                            "lider": 15
                        }
                    ]
                }
            },
        }
    }
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
sacar_miembro_colonia_docs = dict(
    status_code=status.HTTP_200_OK,
    summary="Remover un miembro de una colonia",
    description="""
    Remueve un miembro de una colonia, desasociándolo de la misma.
    
    **Historia de Usuario:**
    Yo como Líder de colonia quiero remover a un miembro de mi colonia 
    para corregir asignaciones incorrectas de vinculación a la colonia.

    **Parámetros requeridos:**
    - **colonia_codigo** (int, path): Código único de la colonia
    - **miembro_id** (int, body): ID del usuario a remover

    **Validaciones y Reglas de Negocio:**

    1. **Usuario debe existir**: El usuario con el ID especificado debe estar registrado en el sistema.
    
    2. **Usuario debe ser miembro de la colonia**: El usuario debe tener `co_codigo == colonia_codigo`.
    
    3. **Usuario no puede estar en Retorno activo**: No se puede remover a un usuario que esté inscrito 
       en un retorno con estado ACTIVO.
    
    4. **No auto-remoción**: El usuario líder no puede removerse a sí mismo de la colonia.

    **Efectos de la operación:**
    - Se desasocia al usuario de la colonia (se establece `co_codigo = NULL`)
    - El usuario pierde acceso a la colonia
    - Otros datos del usuario permanecen sin cambios

    **Nota:** Este endpoint requiere autenticación y rol de líder (pendiente de implementar).
    """,
    responses={
        200: {
            "description": "Miembro removido exitosamente de la colonia.",
            "content": {
                "application/json": {
                    "example": {
                        "mensaje": "El usuario Ana Quira ha sido removido exitosamente de la colonia.",
                        "usuario": {
                            "id": 2,
                            "nombre": "Ana",
                            "apellido": "Quira",
                            "codigo_colonia": None,
                            "documento": "1061692075",
                            "tipo_doc": "CC",
                            "genero": "F",
                            "fecha_nacimiento": "2004-10-21",
                            "celular": "+57 3172361353",
                            "correo": "ana.quira@gmail.com",
                            "codigo_rol": 1,
                            "pais": "Colombia"
                        }
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
            "description": "Conflicto de negocio - No se puede remover al usuario.",
            "content": {
                "application/json": {
                    "examples": {
                        "usuario_no_es_miembro": {
                            "summary": "Usuario no pertenece a la colonia",
                            "value": {"detail": "El usuario con ID 2 no es miembro de la colonia con ID 1."},
                            "description": "**Criterio de aceptación 5**: El usuario seleccionado no pertenece a tu colonia."
                        },
                        "usuario_inscrito_retorno_activo": {
                            "summary": "Usuario inscrito en Retorno activo",
                            "value": {"detail": "El usuario con ID 2 está inscrito en un retorno activo y no puede ser sacado de la colonia."},
                            "description": "**Criterio de aceptación 2**: El usuario está inscrito en un Retorno activo."
                        },
                        "auto_remocion": {
                            "summary": "Intento de auto-remoción",
                            "value": {"detail": "No puedes removerte a ti mismo de la colonia"},
                            "description": "**Criterio de aceptación 7**: El usuario es el líder e intenta removerse a sí mismo."
                        },
                    }
                }
            },
        },
        422: {
            "description": "Body inválido o campos faltantes.",
            "content": {
                "application/json": {
                    "example": {
                        "detail": [
                            {
                                "loc": ["body", "miembro_id"],
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
