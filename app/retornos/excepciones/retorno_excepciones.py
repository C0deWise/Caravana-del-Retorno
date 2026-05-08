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