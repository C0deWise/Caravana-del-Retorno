from fastapi import HTTPException, status

from app.multimedia.config import EXTENSIONES_IMAGEN, EXTENSIONES_VIDEO


class TipoArchivoNoValidoError(HTTPException):
    def __init__(self):
        extensiones_imagen = ','.join(EXTENSIONES_IMAGEN)
        extensiones_video = ','.join(EXTENSIONES_VIDEO)
        super().__init__(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = f"Tipo de archivo no permitido. Solo se permiten: "
                f"imágenes ({extensiones_imagen}) o "
                f"videos ({extensiones_video})"
        )

class RetornoNoExistenteError(HTTPException):
    def __init__(self, codigo_retorno: int):
        super().__init__(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = f"El retorno con código {codigo_retorno} no existe."
        )

class ErrorCargaArchivo(HTTPException):
    def __init__(self):
        super().__init__(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail = "Ocurrió un error al cargar el contenido. Por favor, inténtalo nuevamente."
        )