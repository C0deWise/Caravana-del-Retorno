from fastapi import HTTPException, status

class SolicitudNoEncontrada(Exception):
    pass

class SolicitudEstadoInvalido(Exception):
    pass

class ColoniaNoExistente(HTTPException):
    def __init__(self, colonia_id):
        self.colonia_id = colonia_id
        super().__init__(
            status_code= status.HTTP_404_NOT_FOUND,
            detail=f"Colonia con ID {colonia_id} no encontrada.")
        
class ColoniaInactiva(HTTPException):
    def __init__(self, colonia_id):
        self.colonia_id = colonia_id
        super().__init__(
            status_code= status.HTTP_409_CONFLICT,
            detail=f"La colonia con ID {colonia_id} ya está inactiva.")