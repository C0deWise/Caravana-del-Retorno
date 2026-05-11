from fastapi import HTTPException, status

class RetornoNoExistenteError(HTTPException):
    def __init__(self, retorno_id: int):
        self.retorno_id = retorno_id
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"El retorno con ID {retorno_id} no existe."
        )

class UsuarioNoExistenteError(HTTPException):
    def __init__(self, usuario_id: int):
        self.usuario_id = usuario_id
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"El usuario con ID {usuario_id} no existe."
        )

class PublicacionNoExistenteError(HTTPException):
    def __init__(self, publicacion_id: int):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"La publicación con ID {publicacion_id} no existe."
        )   