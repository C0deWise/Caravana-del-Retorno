from fastapi import HTTPException, status


class SolicitudNoEncontrada(Exception):
    pass

class SolicitudEstadoInvalido(Exception):
    pass

class UsuarioNoEncontrado(HTTPException):
    def __init__(self, usuario_id: int):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"El usuario con código {usuario_id} no existe."
        )

class ColoniaNoEncontrada(HTTPException):
    def __init__(self, colonia_id: int):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"La colonia con código {colonia_id} no existe."
        )