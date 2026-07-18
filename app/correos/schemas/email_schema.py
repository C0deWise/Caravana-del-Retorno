"""
Schemas (DTOs) del módulo de correos.
"""
from typing import Dict, List, Optional

from pydantic import BaseModel, EmailStr, Field


class PasswordRecoveryRequestSchema(BaseModel):
    """Payload que llega desde el cliente para iniciar la recuperación de contraseña."""

    email: EmailStr = Field(..., description="Correo del usuario que solicita el cambio de contraseña")
    reset_url: str = Field(..., description="Enlace completo de restablecimiento con el token real")
    username: Optional[str] = Field(default=None, description="Nombre del usuario destinatario")
    expires_in_minutes: int = Field(default=30, description="Minutos de expiración informados en el correo")
    recovery_token: Optional[str] = Field(default=None, description="Token de recuperación enviado como respaldo textual")

    class Config:
        schema_extra = {
            "example": {
                "email": "usuario@example.com",
                "reset_url": "https://tu-frontend.com/auth/restablecer-contrasena?token=abc123",
                "username": "Usuario",
                "expires_in_minutes": 30,
                "recovery_token": "abc123",
            }
        }


class EmailSchema(BaseModel):
    """
    Payload genérico para el envío de correos con plantilla.

    Se mantiene disponible para otros casos de uso del módulo
    (bienvenida, notificaciones, etc.), no solo recuperación de contraseña.
    """

    email: List[EmailStr] = Field(..., description="Lista de destinatarios")
    subject: str = Field(..., description="Asunto del correo")
    body: Dict[str, str] = Field(..., description="Variables que se inyectan en la plantilla HTML")

    class Config:
        schema_extra = {
            "example": {
                "email": ["usuario@example.com"],
                "subject": "Bienvenido",
                "body": {
                    "title": "Bienvenido",
                    "message": "Gracias por registrarte",
                },
            }
        }


class EmailSendResponseSchema(BaseModel):
    """Respuesta estándar de los endpoints de este módulo."""

    message: str
    sent_to: Optional[List[EmailStr]] = None
