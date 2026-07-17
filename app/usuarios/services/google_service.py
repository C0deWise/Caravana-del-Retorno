"""
Servicio para la vinculación y desvinculación de cuentas de Google.
Utiliza google-auth para verificar los id_token emitidos por Google Identity Services.
"""

from datetime import datetime, timezone

from google.oauth2 import id_token as google_id_token
from google.auth.transport import requests as google_requests
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.usuarios.models.usuario import Usuario


class GoogleServiceError(ValueError):
    """Error controlado para operaciones de vinculación con Google."""


class GoogleService:
    """Servicio para gestionar la vinculación de cuentas de Google."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def verificar_google_token(self, token: str) -> dict:
        """
        Verifica un id_token de Google y retorna los datos del usuario.

        Args:
            token: El id_token recibido de Google Identity Services.

        Returns:
            dict con 'google_id', 'email', 'name'.

        Raises:
            GoogleServiceError: Si el token es inválido o expirado.
        """
        settings = get_settings()
        client_id = settings.GOOGLE_CLIENT_ID

        if not client_id:
            raise GoogleServiceError(
                "La configuración de Google OAuth no está completa. "
                "Configura GOOGLE_CLIENT_ID en el archivo .env"
            )

        try:
            id_info = google_id_token.verify_oauth2_token(
                token,
                google_requests.Request(),
                client_id,
            )
        except Exception as exc:
            raise GoogleServiceError("Token de Google inválido o expirado.") from exc

        google_id = id_info.get("sub")
        email = id_info.get("email")
        name = id_info.get("name", "")

        if not google_id or not email:
            raise GoogleServiceError(
                "El token de Google no contiene la información requerida."
            )

        return {
            "google_id": google_id,
            "email": email.strip().lower(),
            "name": name,
        }

    async def verificar_email_no_vinculado(
        self, google_email: str, exclude_user_id: int
    ) -> None:
        """
        Verifica que el email de Google no esté vinculado a otra cuenta de usuario.

        Args:
            google_email: Email de Google a verificar.
            exclude_user_id: ID del usuario actual (para excluirlo de la búsqueda).

        Raises:
            GoogleServiceError: Si el email ya está vinculado a otra cuenta.
        """
        result = await self.db.execute(
            select(Usuario).where(
                Usuario.us_google_email == google_email,
                Usuario.us_codigo != exclude_user_id,
            )
        )
        existing = result.scalar_one_or_none()

        if existing:
            raise GoogleServiceError(
                "Este correo de Google ya está vinculado a otra cuenta del sistema."
            )

    async def vincular(self, usuario: Usuario, google_data: dict) -> Usuario:
        """
        Vincula una cuenta de Google a un usuario existente.

        Args:
            usuario: El usuario al que se le vinculará la cuenta de Google.
            google_data: Datos verificados de Google (google_id, email, name).

        Returns:
            El usuario actualizado.
        """
        await self.verificar_email_no_vinculado(
            google_data["email"], usuario.us_codigo
        )

        usuario.us_google_id = google_data["google_id"]
        usuario.us_google_email = google_data["email"]
        usuario.us_google_linked_at = datetime.now(timezone.utc)

        await self.db.commit()
        await self.db.refresh(usuario)
        return usuario

    async def desvincular(self, usuario: Usuario) -> Usuario:
        """
        Desvincula la cuenta de Google de un usuario.

        Args:
            usuario: El usuario al que se le desvinculará la cuenta de Google.

        Returns:
            El usuario actualizado.
        """
        usuario.us_google_id = None
        usuario.us_google_email = None
        usuario.us_google_linked_at = None

        await self.db.commit()
        await self.db.refresh(usuario)
        return usuario
