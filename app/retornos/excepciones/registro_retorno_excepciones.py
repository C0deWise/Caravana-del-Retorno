"""
Modulo que define las excepciones personalizadas para el proceso de registro a un retorno.
Contiene las clases de excepciones que se lanzan en el servicio de registro a un retorno 
para manejar errores específicos como retornos no existentes, usuarios no existentes, 
usuarios sin colonia, y usuarios ya registrados. 
"""

from fastapi import HTTPException, status

class RetornoNoExistente(HTTPException):
    def __init__(self, retorno_id: int):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"El retorno con código {retorno_id} no existe."
        )

class RetornoEstadoInvalido(HTTPException):
    def __init__(self, retorno_id: int, retorno_estado: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"No es posible inscribir en el retorno con código {retorno_id} porque su estado es '{retorno_estado}'."
        )

class RetornoEstadoFinalizadoDarseDeBaja(HTTPException):
    def __init__(self, retorno_id: int):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"No es posible darse de baja en el retorno con código {retorno_id} porque ya ha finalizado."
        )
class UsuarioNoExistente(HTTPException):
    def __init__(self, usuario_id: int):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"El usuario con código {usuario_id} no existe."
        )

class UsuarioNoRegistradoEnRetorno(HTTPException):
    def __init__(self, usuario_id: int, retorno_id: int):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"El usuario con código {usuario_id} no está registrado en el retorno con código {retorno_id}."
        )

class UsuarioSinColonia(HTTPException):
    def __init__(self, usuario_id: int):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El usuario con código {usuario_id} no pertenece a ninguna colonia."
        )

class UsuarioYaRegistrado(HTTPException):
    def __init__(self, usuario_id: int, retorno_id: int):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"El usuario con código {usuario_id} ya está registrado en el retorno con código {retorno_id}."
        )