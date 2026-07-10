from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.usuarios.schemas.usuario_esquemas import PasswordResetRequest
from app.usuarios.services.usuario_servicio import UsuarioServicio


class FakeEmailService:
    def __init__(self) -> None:
        self.send_password_recovery_email = AsyncMock()


@pytest.mark.asyncio
async def test_solicitar_recuperacion_no_falla_si_usuario_no_existe():
    repositorio = MagicMock()
    repositorio.buscar_por_correo = AsyncMock(return_value=None)
    email_service = FakeEmailService()
    servicio = UsuarioServicio(repositorio, email_service=email_service)

    await servicio.solicitar_recuperacion_contrasenia("nadie@example.com")

    repositorio.buscar_por_correo.assert_awaited_once_with("nadie@example.com")
    email_service.send_password_recovery_email.assert_not_awaited()


@pytest.mark.asyncio
async def test_solicitar_recuperacion_envia_enlace_con_token():
    usuario = SimpleNamespace(us_codigo=7, us_correo="ana@example.com", us_nombre="Ana")
    repositorio = MagicMock()
    repositorio.buscar_por_correo = AsyncMock(return_value=usuario)
    repositorio.revocar_tokens_recuperacion_activos = AsyncMock()
    repositorio.crear_token_recuperacion = AsyncMock()
    email_service = FakeEmailService()
    servicio = UsuarioServicio(repositorio, email_service=email_service)

    await servicio.solicitar_recuperacion_contrasenia("ana@example.com")

    repositorio.revocar_tokens_recuperacion_activos.assert_awaited_once_with(7)
    repositorio.crear_token_recuperacion.assert_awaited_once()
    email_service.send_password_recovery_email.assert_awaited_once()
    kwargs = email_service.send_password_recovery_email.await_args.kwargs
    assert kwargs["email"] == "ana@example.com"
    assert "/auth/restablecer-contrasena?token=" in kwargs["reset_url"]
    assert kwargs["recovery_token"]


def test_password_reset_request_valida_confirmacion():
    with pytest.raises(ValueError, match="no coincide"):
        PasswordResetRequest(
            token="token",
            nueva_contrasenia="NuevaClave1!",
            confirmar_contrasenia="OtraClave1!",
        )