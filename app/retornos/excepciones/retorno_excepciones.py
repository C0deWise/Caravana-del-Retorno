"""
Excepciones personalizadas para el módulo Retorno.
Centraliza el manejo de errores con códigos HTTP uniformes.
"""

from datetime import date

from fastapi import HTTPException, status


class RetornoNotFoundError(HTTPException):
    """Se lanza cuando no se encuentra un retorno con el código dado."""
    def __init__(self, codigo: int):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Retorno con código {codigo} no encontrado."
        )

class RegistroIndividualParqueaderoExcedidoError(HTTPException):
    """Se lanza cuando se intenta registrar más de un parqueadero para un usuario."""
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El usuario solo puede registrar un parqueadero."
        )

class RetornoAnioDuplicadoError(HTTPException):
    """Se lanza cuando ya existe un retorno para el año seleccionado."""
    def __init__(self, anio: int):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Ya existe un evento de El Retorno para el año seleccionado: {anio}."
        )


class RetornoAnioPasadoError(HTTPException):
    """Se lanza cuando el año proporcionado es anterior al año actual del sistema."""
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="No es posible crear un evento de El Retorno en un año anterior al actual."
        )

class RetornoEstadoActivoaFinalizadoError(HTTPException):
    """Se lanza cuando se intenta finalizar un retorno que está activo."""
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se puede finalizar un retorno que está activo."
        )

class RetornoVigenteError(HTTPException):
    """Se lanza cuando se intenta crear un nuevo retorno mientras otro está vigente."""
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se puede crear un nuevo retorno mientras otro está vigente."
        )
class RetornoEstadoEnCursoaActivoError(HTTPException):
    """Se lanza cuando se intenta reactivar un retorno que está en curso."""
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se puede reactivar un retorno que está en curso."
        )

class RetornoEstadoFinalizadoError(HTTPException):
    """Se lanza cuando se intenta cambiar el estado de un retorno que ya está finalizado."""
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se puede cambiar el estado de un retorno que ya está finalizado."
        )

class RetornoTransicionNoPermitidaError(HTTPException):
    """Base para transiciones no permitidas"""
    def __init__(self, estado_actual: str, nuevo_estado: str, razon: str = None):
        detail = f"No se puede cambiar de estado '{estado_actual}' a '{nuevo_estado}'."
        if razon:
            detail += f" {razon}"
        
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail
        )

class RetornoYaEnEstadoSolicitadoError(HTTPException):
    """Se lanza cuando se intenta cambiar a un estado que ya tiene el retorno."""
    def __init__(self, estado: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El retorno ya se encuentra en estado '{estado}'. "
            f"No es necesario cambiar de estado."
        )