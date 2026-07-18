"""
Documentación para los endpoints de publicaciones.
Este módulo contiene la documentación centralizada para todos los endpoints
relacionados con publicaciones, incluyendo descripciones, ejemplos, validaciones
y códigos de error. La documentación se utiliza en los decoradores de FastAPI
para generar la documentación interactiva en Swagger.
"""

from fastapi import status

APPLICATION_JSON = "application/json"

# ==================== CREAR PUBLICACIÓN ====================

crear_publicacion_docs = {
    "summary": "Crear una nueva publicación",
    "description": """
    Crear una nueva publicación en el sistema.
    
    Esta operación permite a los usuarios crear una nueva publicación asociada a un retorno específico.
    La publicación puede incluir archivos multimedia (imágenes, videos o documentos).
    
    **Validaciones:**
    - El retorno debe existir en el sistema
    - El usuario autor debe existir en el sistema
    - Se puede adjuntar uno o más archivos multimedia
    - Los formatos soportados son: 
      - Imágenes: JPG, JPEG, PNG, GIF
      - Videos: MP4, AVI, MOV, MKV
      - Documentos: PDF
    
    **Ejemplo de uso:**
    ```
    POST /api/v1/crear-publicacion/
    Content-Type: multipart/form-data
    
    retorno_id: 1
    autor: 1
    titulo: Mi experiencia en la Caravana
    resena: Una experiencia transformadora
    archivos: [imagen1.png, imagen2.jpg]
    ```
    
    **Respuesta exitosa (201):**
    - Publicación creada con código único
    - Nombre completo del autor en `nombre_autor`
    - Timestamp de creación automático
    - Lista de multimedia asociado
    """,
    "tags": ["Publicaciones"],
    "status_code": status.HTTP_201_CREATED,
    "responses": {
        201: {
            "description": "Publicación creada exitosamente",
            "content": {
                APPLICATION_JSON: {
                    "example": {
                        "codigo": 1,
                        "retorno": 1,
                        "autor": 1,
                        "nombre_autor": "Juan Perez",
                        "titulo": "Mi experiencia en la Caravana",
                        "resena": "Una experiencia transformadora",
                        "fecha_creacion": "2026-05-11T05:53:28.658880",
                        "multimedia_lista": [
                            {
                                "codigo": 1,
                                "publicacion": 1,
                                "tipo": "imagen",
                                "formato": "png",
                                "url": "/app/multimedia/retorno_1/image.png",
                                "descripcion": "image.png"
                            }
                        ]
                    }
                }
            }
        },
        404: {
            "description": "Retorno o usuario no encontrado",
            "content": {
                APPLICATION_JSON: {
                    "examples": {
                        "retorno_no_existe": {
                            "value": {"detail": "El retorno con ID 99 no existe."}
                        },
                        "usuario_no_existe": {
                            "value": {"detail": "El usuario con ID 99 no existe."}
                        }
                    }
                }
            }
        },
        422: {
            "description": "Error de validación en los datos",
            "content": {
                APPLICATION_JSON: {
                    "example": {
                        "detail": [
                            {
                                "type": "greater_than",
                                "loc": ["body", "retorno_id"],
                                "msg": "Input should be greater than 0",
                                "input": -1
                            }
                        ]
                    }
                }
            }
        }
    }
}

# ==================== OBTENER PUBLICACIONES POR RETORNO ====================

obtener_publicaciones_retorno_docs = {
    "summary": "Obtener publicaciones de un retorno",
    "description": """
    Obtener todas las publicaciones asociadas a un retorno.
    
    Esta operación devuelve una lista de todas las publicaciones creadas en un retorno específico,
    incluyendo los archivos multimedia asociados a cada una.
    
    **Parámetros:**
    - `retorno_id`: ID del retorno (debe ser un número entero positivo)
    
    **Respuesta:**
    - Lista de publicaciones del retorno (vacía si no hay publicaciones)
    - Cada publicación incluye:
            - Información básica (código, título, reseña, autor y nombre del autor)
      - Fecha de creación
      - Lista de archivos multimedia asociados
    
    **Ejemplo de respuesta:**
    Si el retorno con ID 1 tiene 2 publicaciones, la respuesta será una lista con ambas.
    Si no hay publicaciones, devuelve una lista vacía `[]`.
    
    **Casos de uso:**
    - Obtener todas las historias de un retorno específico
    - Mostrar publicaciones en la página de detalles del retorno
    - Listar experiencias compartidas en la Caravana
    """,
    "tags": ["Publicaciones"],
    "status_code": status.HTTP_200_OK,
    "responses": {
        200: {
            "description": "Lista de publicaciones obtenida exitosamente",
            "content": {
                APPLICATION_JSON: {
                    "example": [
                        {
                            "codigo": 1,
                            "retorno": 1,
                            "autor": 1,
                            "nombre_autor": "Juan Perez",
                            "titulo": "Mi experiencia en la Caravana",
                            "resena": "Una experiencia transformadora",
                            "fecha_creacion": "2026-05-11T05:53:28.658880",
                            "multimedia_lista": [
                                {
                                    "codigo": 1,
                                    "publicacion": 1,
                                    "tipo": "imagen",
                                    "formato": "png",
                                    "url": "/app/multimedia/retorno_1/image.png",
                                    "descripcion": "image.png"
                                }
                            ]
                        },
                        {
                            "codigo": 2,
                            "retorno": 1,
                            "autor": 2,
                            "nombre_autor": "Maria Gomez",
                            "titulo": "Otra publicación",
                            "resena": "Más experiencias",
                            "fecha_creacion": "2026-05-11T06:00:00.000000",
                            "multimedia_lista": []
                        }
                    ]
                }
            }
        }
    }
}