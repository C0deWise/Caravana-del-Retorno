"""
Módulo de excepciones personalizadas para el manejo de errores específicos en el módulo de notificaciones.
"""

from fastapi import status
from app.excepciones import AppException


class UsuarioNoEncontradoNotificacion(AppException):
    def __init__(self, usuario_id: int):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No se encontró el usuario con ID {usuario_id}"
        )

class NotificacionNoEncontrada(AppException):
    def __init__(self, notificacion_id: int):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No se encontró la notificación con ID {notificacion_id}"
        )

class NotificacionesNoEncontradasLote(AppException):
    def __init__(self, ids_no_encontrados: list[int]):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Notificaciones no encontradas para los IDs: {ids_no_encontrados}"
        )
