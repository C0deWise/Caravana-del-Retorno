from fastapi import HTTPException, status

class RetornoNoExistente(HTTPException):
    def __init__(self, retorno_id: int):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"El retorno con código {retorno_id} no existe."
        )

class RetornoEstadoFinalizado(HTTPException):
    def __init__(self, retorno_id: int):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"No es posible inscribir en el retorno con código {retorno_id} porque ya ha finalizado."
        )

class UsuarioNoExistente(HTTPException):
    def __init__(self, usuario_id: int):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"El usuario con código {usuario_id} no existe."
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