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
        
class ColoniaSinLiderAsignado(HTTPException):
    def __init__(self, colonia_id):
        self.colonia_id = colonia_id
        super().__init__(
            status_code= status.HTTP_409_CONFLICT,
            detail=f"La colonia con ID {colonia_id} no tiene un líder asignado.")
        
class UsuarioNoExistente(HTTPException):
    def __init__(self, usuario_id):
        self.usuario_id = usuario_id
        super().__init__(
            status_code= status.HTTP_404_NOT_FOUND,
            detail=f"Usuario con ID {usuario_id} no encontrado.")

class UsuarioNoEsMiembroColonia(HTTPException):
    def __init__(self, usuario_id, colonia_id):
        self.usuario_id = usuario_id
        self.colonia_id = colonia_id
        super().__init__(
            status_code= status.HTTP_409_CONFLICT,
            detail=f"El usuario con ID {usuario_id} no es miembro de la colonia con ID {colonia_id}.")

class UsuarioYaEsLider(HTTPException):
    def __init__(self, usuario_id, colonia_id):
        self.usuario_id = usuario_id
        self.colonia_id = colonia_id
        super().__init__(
            status_code= status.HTTP_409_CONFLICT,
            detail=f"El usuario con ID {usuario_id} ya es líder actual de la colonia con ID {colonia_id}.")
    