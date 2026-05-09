from fastapi import status

cargar_contenido_multimedia_docs = {
    "summary": "Cargar contenido multimedia para un retorno",
    "description": "Permite cargar un archivo multimedia (imagen o video) asociado a un retorno específico.",
    "status_code": status.HTTP_201_CREATED,
    "responses": {
        201: {
            "description": "Contenido multimedia cargado exitosamente.",
            "content": {
                "application/json": {
                    "example": {
                        "codigo": 1,
                        "retorno": 1,
                        "tipo": "imagen",
                        "url": "https://storage.example.com/multimedia/imagen1.jpg",
                        "nombre_archivo": "imagen1.jpg",
                        "fecha_creacion": "2026-03-15"
                    }
                }
            },
        },
    },
}
