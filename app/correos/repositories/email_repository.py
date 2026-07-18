"""
Capa de infraestructura (repository): conexión y envío real de correos
vía SMTP usando fastapi-mail.
"""
from pathlib import Path

from decouple import config
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema

from app.correos.excepciones.email_exceptions import EmailSendException
from app.correos.models.email import EmailMessage

# correos/repositories/email_repository.py -> correos/plantillas/email
TEMPLATE_FOLDER = Path(__file__).resolve().parent.parent / "plantillas" / "email"


def _build_connection_config() -> ConnectionConfig:
    return ConnectionConfig(
        MAIL_USERNAME=config("MAIL_USERNAME"),
        MAIL_PASSWORD=config("MAIL_PASSWORD"),
        MAIL_FROM=config("MAIL_FROM"),
        MAIL_PORT=config("MAIL_PORT", cast=int),
        MAIL_SERVER=config("MAIL_SERVER"),
        MAIL_STARTTLS=config("MAIL_TLS", cast=bool, default=True),
        MAIL_SSL_TLS=config("MAIL_SSL", cast=bool, default=False),
        USE_CREDENTIALS=config("USE_CREDENTIALS", cast=bool, default=True),
        VALIDATE_CERTS=config("VALIDATE_CERTS", cast=bool, default=True),
        TEMPLATE_FOLDER=TEMPLATE_FOLDER,
    )


class EmailRepository:
    """Wrapper de fastapi-mail. Traduce fallos de infraestructura a excepciones de dominio."""

    def __init__(self) -> None:
        self._conf = _build_connection_config()

    async def send(self, message: EmailMessage) -> None:
        try:
            fm = FastMail(self._conf)
            mail_message = MessageSchema(
                subject=message.subject,
                recipients=message.recipients,
                template_body=message.context,
                subtype=message.subtype,
            )
            await fm.send_message(mail_message, template_name=message.template_name)
        except Exception as error:  # noqa: BLE001 - se traduce a excepción de dominio
            raise EmailSendException(
                f"No fue posible enviar el correo a {message.recipients}: {error}",
                original_error=error,
            ) from error
