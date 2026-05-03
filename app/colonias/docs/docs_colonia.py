"""
Documentación para la función de desactivación de una colonia.
"""

from fastapi import status

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
)