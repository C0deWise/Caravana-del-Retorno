"""
Excepciones personalizadas para el módulo Retorno.
Centraliza el manejo de errores con códigos HTTP uniformes.
"""

from fastapi import HTTPException, status


class RetornoNotFoundError(HTTPException):
    """Se lanza cuando no se encuentra un retorno con el código dado."""
    def __init__(self, codigo: int):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Retorno con código {codigo} no encontrado."
        )