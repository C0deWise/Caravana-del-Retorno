"""
Modulo de excepciones para la gestión de multimedia en la aplicación. Contiene las clases de excepción personalizadas
que se lanzan en el servicio de multimedia para manejar errores específicos como tipos de archivos no válidos y errores
al cargar archivos. Estas excepciones permiten proporcionar respuestas claras y específicas a los clientes de la API
cuando ocurren errores relacionados con la gestión de multimedia.
"""

from fastapi import HTTPException, status

from app.multimedia.config import EXTENSIONES_POR_TIPO


class TipoArchivoNoValidoError(HTTPException):
    def __init__(self):
        extensiones_imagen = ','.join(EXTENSIONES_POR_TIPO.get("imagen", []))
        extensiones_video = ','.join(EXTENSIONES_POR_TIPO.get("video", []))
        extensiones_documento = ','.join(EXTENSIONES_POR_TIPO.get("documento", []))
        super().__init__(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = f"Tipo de archivo no permitido. Solo se permiten: "
                f"imágenes ({extensiones_imagen}) o "
                f"videos ({extensiones_video}) o "
                f"documentos ({extensiones_documento})"
        )

class ErrorCargaArchivo(HTTPException):
    def __init__(self):
        super().__init__(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail = "Ocurrió un error al cargar el contenido. Por favor, inténtalo nuevamente."
        )