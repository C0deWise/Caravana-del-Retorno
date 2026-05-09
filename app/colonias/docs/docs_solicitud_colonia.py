"""
    docs_solicitud_colonia.py - Documentación de los endpoints relacionados con las solicitudes de ingreso a colonias.
"""

from fastapi import status

# ─────────────────────────────────────────
#  POST /crear-solicitud
# ─────────────────────────────────────────
crear_solicitud_docs = dict(
    summary="Crear una solicitud de ingreso a una colonia",
    description="Crea una nueva solicitud de ingreso a una colonia con el código de usuario y el código de colonia.",
    status_code=status.HTTP_201_CREATED,
    responses={
        200: {
            "description": "Miembro registrado exitosamente.",
            "content": {
                "application/json": {
                    "example": {
                        "codigo_usuario": 10,
                        "nombre_usuario": "Juan",
                        "apellido_usuario": "Pérez",
                        "codigo_colonia": 5,
                    }
                }
            },
        },
        201: {
            "description": "Solicitud creada exitosamente.",
            "content": {
                "application/json": {
                    "example": {
                        "codigo": 1,
                        "estado": "pendiente",
                        "fecha_creacion": "2026-03-15T21:00:00",
                        "codigo_usuario": 10,
                        "nombre_usuario": "Juan",
                        "apellido_usuario": "Pérez",
                        "codigo_colonia": 5,
                    }
                }
            },
        },
        404: {
            "description": "El usuario con el código especificado no existe.",
            "content": {
                "application/json": {
                    "example": {"detail": "El usuario con código 10 no existe."}
                }
            },
        },
        422: {
            "description": "Error de validación en los datos enviados.",
        },
    },
)

# ─────────────────────────────────────────
#  GET /solicitudes-pendientes/{cod_colonia}
# ─────────────────────────────────────────
obtener_solicitudes_pendientes_docs = dict(
    summary="Obtener solicitudes de ingreso pendientes",
    description=(
        "Obtiene una lista de todas las solicitudes de ingreso a una colonia específica "
        "que están pendientes de revisión."
    ),
    status_code=status.HTTP_200_OK,
    responses={
        200: {
            "description": "Lista de solicitudes pendientes.",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "codigo": 1,
                            "estado": "pendiente",
                            "fecha_creacion": "2026-03-15T21:00:00",
                            "codigo_usuario": 10,
                            "nombre_usuario": "Juan",
                            "apellido_usuario": "Pérez",
                            "codigo_colonia": 5,
                        }
                    ]
                }
            },
        },
        404: {
            "description": "No se encontraron solicitudes pendientes para la colonia indicada.",
            "content": {
                "application/json": {
                    "example": {"detail": "No se encontraron solicitudes pendientes para la colonia 5."}
                }
            },
        },
    },
)

# ─────────────────────────────────────────
#  GET /solicitudes-recientes/{cod_colonia}
# ─────────────────────────────────────────
obtener_solicitudes_recientes_colonia_docs = dict(
    summary="Obtener solicitudes de ingreso recientes por colonia",
    description=(
        "Obtiene una lista de las solicitudes de ingreso a una colonia específica "
        "que han sido creadas en los últimos 30 días."
    ),
    status_code=status.HTTP_200_OK,
    responses={
        200: {
            "description": "Lista de solicitudes recientes de la colonia.",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "codigo": 2,
                            "estado": "aprobada",
                            "fecha_creacion": "2026-03-10T10:30:00",
                            "codigo_usuario": 7,
                            "nombre_usuario": "María",
                            "apellido_usuario": "Gómez",
                            "codigo_colonia": 5,
                        }
                    ]
                }
            },
        },
        404: {
            "description": "No se encontraron solicitudes recientes para la colonia indicada.",
            "content": {
                "application/json": {
                    "example": {"detail": "No se encontraron solicitudes recientes para la colonia 5."}
                }
            },
        },
    },
)

# ─────────────────────────────────────────
#  GET /solicitudes-recientes-usuario/{cod_usuario}
# ─────────────────────────────────────────
obtener_solicitudes_recientes_usuario_docs = dict(
    summary="Obtener solicitudes de ingreso recientes por usuario",
    description=(
        "Obtiene una lista de las solicitudes de ingreso a colonias realizadas por un usuario específico "
        "que han sido creadas en los últimos 30 días."
    ),
    status_code=status.HTTP_200_OK,
    responses={
        200: {
            "description": "Lista de solicitudes recientes del usuario.",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "codigo": 3,
                            "estado": "rechazada",
                            "fecha_creacion": "2026-03-01T08:00:00",
                            "codigo_usuario": 10,
                            "nombre_usuario": "Juan",
                            "apellido_usuario": "Pérez",
                            "codigo_colonia": 3,
                        }
                    ]
                }
            },
        },
        404: {
            "description": "No se encontraron solicitudes recientes para el usuario indicado.",
            "content": {
                "application/json": {
                    "example": {"detail": "No se encontraron solicitudes recientes para el usuario 10."}
                }
            },
        },
    },
)