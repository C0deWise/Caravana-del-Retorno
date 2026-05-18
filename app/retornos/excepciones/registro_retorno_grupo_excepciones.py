"""
Módulo de excepciones para el registro de retornos en grupo.
Contiene las clases de excepciones que se lanzan en el servicio de registro de retornos en grupo 
para manejar errores específicos como retornos no existentes, y retornos no activos.
"""

from fastapi import HTTPException, status

class RetornoNoExistente(HTTPException):
    def __init__(self, retorno_id: int):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"El retorno con código {retorno_id} no existe."
        )

class RetornoNoActivo(HTTPException):
    def __init__(self, retorno_id: int, retorno_estado: str):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"No es posible incribirse en el retorno con código {retorno_id} porque su estado es {retorno_estado}."
        )

class RegistroGrupoRetornoNoExiste(HTTPException):
    def __init__(self, registro_id: int):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"El registro de retorno en grupo con código {registro_id} no existe."
        )

class RegistroGrupoRetornoNoExistente(HTTPException):
    def __init__(self, grupo_id: int, retorno_id: int):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No existe un registro para el grupo con código {grupo_id} en el retorno con código {retorno_id}."
        )

class GrupoRetornoNoExistente(HTTPException):
    def __init__(self, grupo_id: int):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"El grupo con código {grupo_id} no existe."
        )