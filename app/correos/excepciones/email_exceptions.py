"""Excepciones propias del módulo de correos."""
from typing import Optional


class EmailModuleException(Exception):
    """Excepción base del módulo de correos."""


class EmailConfigurationException(EmailModuleException):
    """Falta o es inválida la configuración del servidor de correo (variables de entorno)."""


class EmailSendException(EmailModuleException):
    """El envío del correo falló (SMTP, timeout, plantilla inexistente, etc.)."""

    def __init__(self, message: str, original_error: Optional[Exception] = None):
        super().__init__(message)
        self.original_error = original_error
