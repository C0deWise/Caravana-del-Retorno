"""
Capa de servicios (services): reglas de negocio del módulo de correos.
"""
from typing import Dict, List, Optional

from app.correos.models.email import EmailMessage
from app.correos.repositories.email_repository import EmailRepository


class EmailService:
    def __init__(self, repository: Optional[EmailRepository] = None) -> None:
        self._repository = repository or EmailRepository()

    async def send_password_recovery_email(
        self,
        email: str,
        reset_url: str,
        username: str = "",
        expires_in_minutes: int = 30,
        recovery_token: str | None = None,
    ) -> None:
        """
        Envía el correo de recuperación de contraseña.
        """
        message = EmailMessage(
            recipients=[email],
            subject="Recupera tu contraseña",
            template_name="password_recovery.html",
            context={
                "username": username or email,
                "reset_url": reset_url,
                "expires_in_minutes": str(expires_in_minutes),
                "recovery_token": recovery_token or "",
            },
        )
        await self._repository.send(message)

    async def send_generic_email(
        self,
        recipients: List[str],
        subject: str,
        template_name: str,
        context: Dict[str, str],
    ) -> None:
        """Punto de extensión reutilizable para otros correos del sistema (bienvenida, notificaciones, etc.)."""
        message = EmailMessage(
            recipients=recipients,
            subject=subject,
            template_name=template_name,
            context=context,
        )
        await self._repository.send(message)
