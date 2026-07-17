"""
Excepciones base para toda la aplicación.
Define una excepción base con status_code y detail que puede ser
convertida a HTTPResponse por el handler global de excepciones.
"""


class AppException(Exception):
    """Excepción base de la aplicación. Todas las excepciones custom deben heredar de esta."""
    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail
        super().__init__(detail)
