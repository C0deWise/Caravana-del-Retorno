"""
Capa de presentación (API): expone los endpoints HTTP del módulo de
correos.
"""
from fastapi import APIRouter, BackgroundTasks

from app.correos.docs.email_docs import PASSWORD_RECOVERY_DESCRIPTION, PASSWORD_RECOVERY_SUMMARY
from app.correos.schemas.email_schema import EmailSendResponseSchema, PasswordRecoveryRequestSchema
from app.correos.services.email_service import EmailService

router = APIRouter(prefix="/correos", tags=["Correos"])


def get_email_service() -> EmailService:
    return EmailService()


@router.post(
    "/password-recovery",
    summary=PASSWORD_RECOVERY_SUMMARY,
    description=PASSWORD_RECOVERY_DESCRIPTION,
)
async def send_password_recovery_email(
    data: PasswordRecoveryRequestSchema,
    background_tasks: BackgroundTasks,
) -> EmailSendResponseSchema:
    """
    Se ejecuta en background para no bloquear la respuesta al cliente
    mientras se conecta con el servidor SMTP.
    """
    service = get_email_service()

    background_tasks.add_task(
        service.send_password_recovery_email,
        email=data.email,
        reset_url=data.reset_url,
        username=data.username or data.email,
        expires_in_minutes=data.expires_in_minutes,
        recovery_token=data.recovery_token,
    )

    return EmailSendResponseSchema(
        message="Correo de recuperación en proceso de envío",
        sent_to=[data.email],
    )
