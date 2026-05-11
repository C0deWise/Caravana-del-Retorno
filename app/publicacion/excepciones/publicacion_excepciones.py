"""
Modulo de excepciones para la gestión de publicaciones en la aplicación. Contiene las clases de excepción personalizadas
que se lanzan en el servicio de publicaciones para manejar errores específicos como publicaciones no existentes, usuarios
no existentes y retornos no existentes. Estas excepciones permiten proporcionar respuestas claras y específicas a los
clientes de la API cuando ocurren errores relacionados con la gestión de publicaciones.
"""

from fastapi import HTTPException, status

class RetornoNoExistenteError(HTTPException):
    """Excepción que se lanza cuando se intenta crear o consultar una publicación asociada a un retorno que no existe."""
    def __init__(self, retorno_id: int):
        self.retorno_id = retorno_id
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"El retorno con ID {retorno_id} no existe."
        )

class UsuarioNoExistenteError(HTTPException):
    """Excepción que se lanza cuando se intenta crear o consultar una publicación asociada a un usuario que no existe."""
    def __init__(self, usuario_id: int):
        self.usuario_id = usuario_id
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"El usuario con ID {usuario_id} no existe."
        )

class PublicacionNoExistenteError(HTTPException):
    """Excepción que se lanza cuando se intenta consultar una publicación que no existe."""
    def __init__(self, publicacion_id: int):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"La publicación con ID {publicacion_id} no existe."
        )   