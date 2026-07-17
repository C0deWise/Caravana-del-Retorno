"""
Módulo de excepciones personalizadas para el manejo de errores específicos en la aplicación de colonias.
Este módulo define excepciones que pueden ser lanzadas en diferentes partes de la aplicación para indicar 
situaciones específicas, como la no existencia de una colonia, problemas con el estado de una solicitud, o
conflictos relacionados con usuarios y colonias.
"""

from fastapi import status
from app.excepciones import AppException


class SolicitudNoEncontrada(AppException):
    def __init__(self, solicitud_id: int):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Solicitud con código {solicitud_id} no encontrada."
        )

class SolicitudEstadoInvalido(AppException):
    def __init__(self, solicitud_id: int, estado_actual: str):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Solicitud {solicitud_id} está en estado '{estado_actual}'. Solo se pueden procesar solicitudes pendientes."
        )

class UsuarioNoEncontrado(AppException):
    def __init__(self, usuario_id: int):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"El usuario con código {usuario_id} no existe."
        )

class ColoniaNoEncontrada(AppException):
    def __init__(self, colonia_id: int):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"La colonia con código {colonia_id} no existe."
        )

class ColoniaNoExistente(AppException):
    def __init__(self, colonia_id):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Colonia con ID {colonia_id} no encontrada."
        )

class ColoniaInactiva(AppException):
    def __init__(self, colonia_id):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"La colonia con ID {colonia_id} ya está inactiva."
        )

class ColoniaSinLiderAsignado(AppException):
    def __init__(self, colonia_id):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"La colonia con ID {colonia_id} no tiene un líder asignado."
        )

class UsuarioNoExistente(AppException):
    def __init__(self, usuario_id):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usuario con ID {usuario_id} no encontrado."
        )

class UsuarioYaTieneColonia(AppException):
    def __init__(self, usuario_id: int, colonia_actual: int, colonia_nueva: int):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Usuario con ID {usuario_id} pertenece a la colonia {colonia_actual}, no puede ser asignado como lider de la colonia {colonia_nueva}."
        )

class UsuarioNoEsMiembroColonia(AppException):
    def __init__(self, usuario_id, colonia_id):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"El usuario con ID {usuario_id} no es miembro de la colonia con ID {colonia_id}."
        )

class UsuarioYaEsLider(AppException):
    def __init__(self, usuario_id, colonia_id):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"El usuario con ID {usuario_id} ya es líder actual de la colonia con ID {colonia_id}."
        )

class UsuarioInscritoRetornoActivo(AppException):
    def __init__(self, usuario_id):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"El usuario con ID {usuario_id} no puede ser removido de la colonia porque esta inscrito en retornos activos."
        )

class AutoRemocionUsuarioColonia(AppException):
    def __init__(self, usuario_id):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                f"El usuario con ID {usuario_id} es el líder actual de la colonia y no puede removerse a sí mismo. "
                f"Para remover al líder, primero debe asignar un nuevo líder a la colonia."
            )
        )

class ColoniaUbicacionDuplicada(AppException):
    def __init__(self, detalle: str):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=detalle
        )
