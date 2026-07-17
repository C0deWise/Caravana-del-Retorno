"""
    password_recovery_tests.py contiene las pruebas para los endpoints y servicio
    relacionados con la recuperación y restablecimiento de contraseña:
      - POST /api/v1/usuario/forgot-password
      - POST /api/v1/usuario/reset-password
    Cubre: validaciones de esquema Pydantic, lógica de negocio del servicio
    y respuestas HTTP (usando TestClient con dependencias mockeadas).
"""

import pytest
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.correos.excepciones.email_exceptions import EmailSendException
from app.usuarios.api.v1.usuario_router import get_usuario_servicio
from app.usuarios.api.v1.usuario_router import router as usuario_router
from app.usuarios.schemas.usuario_esquemas import (
    PasswordRecoveryRequest,
    PasswordResetRequest,
)
from app.usuarios.security import TokenError
from app.usuarios.services.usuario_servicio import UsuarioServicio


# ─── Helpers y fixtures compartidos ──────────────────────────────────────────

CONTRASENIA_SEGURA = "Segura@123"
CONTRASENIA_INSEGURA_CORTA = "abc"
TOKEN_VALIDO = "token.valido.jwt"


def _make_servicio(repositorio=None, email_service=None):
    repo = repositorio or MagicMock()
    return UsuarioServicio(
        repositorio=repo,
        repositorio_parentesco=MagicMock(),
        email_service=email_service,
    )


@pytest.fixture
def repositorio():
    repo = MagicMock()
    repo.buscar_por_correo = AsyncMock(return_value=None)
    repo.revocar_tokens_recuperacion_activos = AsyncMock()
    repo.crear_token_recuperacion = AsyncMock()
    repo.obtener_usuario_por_id = AsyncMock(return_value=None)
    repo.obtener_token_recuperacion_activo = AsyncMock(return_value=None)
    repo.actualizar_contrasenia_con_token = AsyncMock()
    return repo


@pytest.fixture
def email_service():
    svc = MagicMock()
    svc.send_password_recovery_email = AsyncMock()
    return svc


@pytest.fixture
def servicio(repositorio, email_service):
    return _make_servicio(repositorio=repositorio, email_service=email_service)


# ─── App de prueba con dependencias mockeadas ─────────────────────────────────

@pytest.fixture
def mock_servicio():
    svc = MagicMock()
    svc.solicitar_recuperacion_contrasenia = AsyncMock()
    svc.restablecer_contrasenia = AsyncMock()
    return svc


@pytest.fixture
def client(mock_servicio):
    app = FastAPI()
    app.include_router(usuario_router)
    app.dependency_overrides[get_usuario_servicio] = lambda: mock_servicio
    with TestClient(app, raise_server_exceptions=True) as c:
        yield c
    app.dependency_overrides.clear()


# ═════════════════════════════════════════════════════════════════════════════
#  1. Validación de esquemas Pydantic
# ═════════════════════════════════════════════════════════════════════════════

class TestPasswordRecoveryRequestSchema:
    """Valida el esquema de solicitud de recuperación de contraseña."""

    @pytest.mark.parametrize("correo", [
        "usuario@gmail.com",
        "usuario.apellido@empresa.co",
        "usuario+tag@dominio.com",
        "test@sub.dominio.org",
    ])
    def test_correo_valido(self, correo):
        schema = PasswordRecoveryRequest(correo=correo)
        assert schema.correo == correo.strip().lower()

    @pytest.mark.parametrize("correo", [
        "noesuncorreo",
        "sin_arroba.com",
        "@sinlocal.com",
        "sin_extension@dominio",
        "",
        "espacios en@correo.com",
    ])
    def test_correo_invalido_lanza_error(self, correo):
        with pytest.raises(ValueError):
            PasswordRecoveryRequest(correo=correo)

    def test_correo_se_normaliza_a_minusculas(self):
        schema = PasswordRecoveryRequest(correo="Usuario@GMAIL.COM")
        assert schema.correo == "usuario@gmail.com"


class TestPasswordResetRequestSchema:
    """Valida el esquema de restablecimiento de contraseña."""

    def _datos_validos(self, **overrides):
        base = {
            "token": TOKEN_VALIDO,
            "nueva_contrasenia": CONTRASENIA_SEGURA,
            "confirmar_contrasenia": CONTRASENIA_SEGURA,
        }
        base.update(overrides)
        return base

    def test_esquema_valido(self):
        schema = PasswordResetRequest(**self._datos_validos())
        assert schema.token == TOKEN_VALIDO

    def test_token_vacio_lanza_error(self):
        with pytest.raises(ValueError, match="token"):
            PasswordResetRequest(**self._datos_validos(token="   "))

    @pytest.mark.parametrize("contrasenia, error_esperado", [
        ("corta1A!", "8 caracteres"),
        ("sinmayuscula@1", "mayúscula"),
        ("SINMINUSCULA@1", "minúscula"),
        ("SinNumero@xx", "número"),
        ("SinEspecial12", "especial"),
    ])
    def test_contrasenia_invalida_lanza_error(self, contrasenia, error_esperado):
        with pytest.raises(ValueError, match=error_esperado):
            PasswordResetRequest(**self._datos_validos(
                nueva_contrasenia=contrasenia,
                confirmar_contrasenia=contrasenia,
            ))

    def test_confirmacion_diferente_lanza_error(self):
        with pytest.raises(ValueError, match="confirmación"):
            PasswordResetRequest(**self._datos_validos(
                nueva_contrasenia=CONTRASENIA_SEGURA,
                confirmar_contrasenia="Diferente@999",
            ))

    def test_contrasenia_corta_menos_de_8_chars(self):
        with pytest.raises(ValueError):
            PasswordResetRequest(**self._datos_validos(
                nueva_contrasenia=CONTRASENIA_INSEGURA_CORTA,
                confirmar_contrasenia=CONTRASENIA_INSEGURA_CORTA,
            ))


# ═════════════════════════════════════════════════════════════════════════════
#  2. Servicio — solicitar_recuperacion_contrasenia
# ═════════════════════════════════════════════════════════════════════════════

class TestSolicitarRecuperacion:
    """Pruebas unitarias del método solicitar_recuperacion_contrasenia."""

    @pytest.mark.asyncio
    async def test_correo_inexistente_no_lanza_error(self, servicio, repositorio):
        """Si el correo no existe en el sistema, retorna silenciosamente (seguridad)."""
        repositorio.buscar_por_correo = AsyncMock(return_value=None)

        await servicio.solicitar_recuperacion_contrasenia("noexiste@example.com")

        repositorio.buscar_por_correo.assert_awaited_once()
        repositorio.revocar_tokens_recuperacion_activos.assert_not_awaited()
        repositorio.crear_token_recuperacion.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_correo_existente_crea_token_y_envia_correo(
        self, servicio, repositorio, email_service
    ):
        """Cuando el correo existe se revoca token anterior, se crea uno nuevo y se envía correo."""
        usuario_mock = MagicMock()
        usuario_mock.us_codigo = 1
        usuario_mock.us_correo = "test@example.com"
        usuario_mock.us_nombre = "Juan"
        repositorio.buscar_por_correo = AsyncMock(return_value=usuario_mock)

        expires_at = datetime.now(timezone.utc)
        with patch("app.usuarios.services.usuario_servicio.create_password_recovery_token") as mock_cpt, \
             patch("app.usuarios.services.usuario_servicio.get_settings") as mock_settings:
            mock_cpt.return_value = ("tok.abc", "jti_abc", expires_at)
            mock_settings.return_value = MagicMock(
                FRONTEND_URL="https://frontend.test",
                PASSWORD_RECOVERY_TOKEN_EXPIRE_MINUTES=30,
            )

            await servicio.solicitar_recuperacion_contrasenia("test@example.com")

        repositorio.revocar_tokens_recuperacion_activos.assert_awaited_once_with(1)
        repositorio.crear_token_recuperacion.assert_awaited_once()
        email_service.send_password_recovery_email.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_fallo_envio_correo_propaga_excepcion(
        self, servicio, repositorio, email_service
    ):
        """Si el envío de correo falla, la excepción EmailSendException se propaga."""
        usuario_mock = MagicMock()
        usuario_mock.us_codigo = 2
        usuario_mock.us_correo = "fallo@example.com"
        usuario_mock.us_nombre = "Pedro"
        repositorio.buscar_por_correo = AsyncMock(return_value=usuario_mock)
        email_service.send_password_recovery_email = AsyncMock(
            side_effect=EmailSendException("SMTP timeout")
        )

        expires_at = datetime.now(timezone.utc)
        with patch("app.usuarios.services.usuario_servicio.create_password_recovery_token") as mock_cpt, \
             patch("app.usuarios.services.usuario_servicio.get_settings") as mock_settings:
            mock_cpt.return_value = ("tok.fail", "jti_fail", expires_at)
            mock_settings.return_value = MagicMock(
                FRONTEND_URL="https://frontend.test",
                PASSWORD_RECOVERY_TOKEN_EXPIRE_MINUTES=30,
            )

            with pytest.raises(EmailSendException):
                await servicio.solicitar_recuperacion_contrasenia("fallo@example.com")

    @pytest.mark.asyncio
    async def test_correo_se_normaliza_antes_de_buscar(self, servicio, repositorio):
        """El correo se normaliza (trim + lower) antes de consultar al repositorio."""
        repositorio.buscar_por_correo = AsyncMock(return_value=None)

        await servicio.solicitar_recuperacion_contrasenia("  TEST@EXAMPLE.COM  ")

        repositorio.buscar_por_correo.assert_awaited_once_with("test@example.com")


# ═════════════════════════════════════════════════════════════════════════════
#  3. Servicio — restablecer_contrasenia
# ═════════════════════════════════════════════════════════════════════════════

class TestRestablecerContrasenia:
    """Pruebas unitarias del método restablecer_contrasenia."""

    def _payload_valido(self, user_id=1, correo="user@test.com", jti="jti123"):
        return {"sub": str(user_id), "correo": correo, "jti": jti}

    @pytest.mark.asyncio
    async def test_token_invalido_lanza_token_error(self, servicio):
        """Un token JWT mal formado o expirado lanza TokenError."""
        with patch("app.usuarios.services.usuario_servicio.decode_token") as mock_decode:
            mock_decode.side_effect = TokenError("Token invalido o expirado")

            with pytest.raises(TokenError, match="invalido"):
                await servicio.restablecer_contrasenia("token.malo", CONTRASENIA_SEGURA)

    @pytest.mark.asyncio
    async def test_usuario_no_encontrado_lanza_value_error(self, servicio, repositorio):
        """Si el user_id del token no existe en BD, lanza ValueError."""
        repositorio.obtener_usuario_por_id = AsyncMock(return_value=None)

        with patch("app.usuarios.services.usuario_servicio.decode_token") as mock_decode:
            mock_decode.return_value = self._payload_valido()

            with pytest.raises(ValueError, match="válido"):
                await servicio.restablecer_contrasenia(TOKEN_VALIDO, CONTRASENIA_SEGURA)

    @pytest.mark.asyncio
    async def test_correo_no_coincide_lanza_value_error(self, servicio, repositorio):
        """Si el correo del token no coincide con el usuario en BD, lanza ValueError."""
        usuario_mock = MagicMock()
        usuario_mock.us_correo = "otro@correo.com"
        repositorio.obtener_usuario_por_id = AsyncMock(return_value=usuario_mock)

        with patch("app.usuarios.services.usuario_servicio.decode_token") as mock_decode:
            mock_decode.return_value = self._payload_valido(correo="diferente@correo.com")

            with pytest.raises(ValueError, match="válido"):
                await servicio.restablecer_contrasenia(TOKEN_VALIDO, CONTRASENIA_SEGURA)

    @pytest.mark.asyncio
    async def test_token_no_activo_en_bd_lanza_value_error(self, servicio, repositorio):
        """Si el token ya fue usado o no existe en BD, lanza ValueError."""
        usuario_mock = MagicMock()
        usuario_mock.us_correo = "user@test.com"
        repositorio.obtener_usuario_por_id = AsyncMock(return_value=usuario_mock)
        repositorio.obtener_token_recuperacion_activo = AsyncMock(return_value=None)

        with patch("app.usuarios.services.usuario_servicio.decode_token") as mock_decode:
            mock_decode.return_value = self._payload_valido()

            with pytest.raises(ValueError, match="válido"):
                await servicio.restablecer_contrasenia(TOKEN_VALIDO, CONTRASENIA_SEGURA)

    @pytest.mark.asyncio
    async def test_restablecer_exitoso_llama_actualizar(self, servicio, repositorio):
        """Flujo exitoso: actualiza la contraseña en base de datos."""
        usuario_mock = MagicMock()
        usuario_mock.us_codigo = 1
        usuario_mock.us_correo = "user@test.com"
        token_mock = MagicMock()

        repositorio.obtener_usuario_por_id = AsyncMock(return_value=usuario_mock)
        repositorio.obtener_token_recuperacion_activo = AsyncMock(return_value=token_mock)
        repositorio.actualizar_contrasenia_con_token = AsyncMock()

        with patch("app.usuarios.services.usuario_servicio.decode_token") as mock_decode:
            mock_decode.return_value = self._payload_valido()

            await servicio.restablecer_contrasenia(TOKEN_VALIDO, CONTRASENIA_SEGURA)

        repositorio.actualizar_contrasenia_con_token.assert_awaited_once()
        # Verifica que la contraseña se haya hasheado (no se guarda en texto plano)
        args = repositorio.actualizar_contrasenia_con_token.call_args[0]
        nueva_hash = args[1]
        assert nueva_hash != CONTRASENIA_SEGURA
        assert nueva_hash.startswith("$2b$")

    @pytest.mark.asyncio
    async def test_token_sin_jti_lanza_token_error(self, servicio):
        """Un token de recuperación sin campo 'jti' lanza TokenError."""
        with patch("app.usuarios.services.usuario_servicio.decode_token") as mock_decode:
            mock_decode.return_value = {"sub": "1", "correo": "x@x.com"}  # sin jti

            with pytest.raises(TokenError):
                await servicio.restablecer_contrasenia(TOKEN_VALIDO, CONTRASENIA_SEGURA)


# ═════════════════════════════════════════════════════════════════════════════
#  4. Endpoints HTTP — /api/v1/usuario/forgot-password
# ═════════════════════════════════════════════════════════════════════════════

class TestForgotPasswordEndpoint:
    """Pruebas de integración (TestClient) para POST /forgot-password."""

    URL = "/usuario/forgot-password"

    def test_correo_valido_retorna_200(self, client, mock_servicio):
        """Siempre retorna 200 aunque el correo no exista (por seguridad)."""
        mock_servicio.solicitar_recuperacion_contrasenia = AsyncMock()

        resp = client.post(self.URL, json={"correo": "alguien@example.com"})

        assert resp.status_code == 200
        assert "enlace" in resp.json()["mensaje"].lower() or "correo" in resp.json()["mensaje"].lower()

    def test_correo_no_existente_retorna_200_mensaje_generico(self, client, mock_servicio):
        """Aunque el correo no exista, la respuesta es 200 para no revelar qué correos están registrados."""
        mock_servicio.solicitar_recuperacion_contrasenia = AsyncMock(return_value=None)

        resp = client.post(self.URL, json={"correo": "fantasma@example.com"})

        assert resp.status_code == 200

    def test_fallo_smtp_retorna_503(self, client, mock_servicio):
        """Si el servicio de correo falla, el endpoint devuelve 503."""
        mock_servicio.solicitar_recuperacion_contrasenia = AsyncMock(
            side_effect=EmailSendException("SMTP caído")
        )

        resp = client.post(self.URL, json={"correo": "usuario@example.com"})

        assert resp.status_code == 503

    def test_correo_invalido_retorna_422(self, client):
        """Un correo con formato inválido produce un error 422 de validación."""
        resp = client.post(self.URL, json={"correo": "esto-no-es-correo"})

        assert resp.status_code == 422

    def test_correo_vacio_retorna_422(self, client):
        """Un correo vacío produce un error 422 de validación."""
        resp = client.post(self.URL, json={"correo": ""})

        assert resp.status_code == 422

    def test_cuerpo_vacio_retorna_422(self, client):
        """Sin cuerpo JSON retorna 422."""
        resp = client.post(self.URL, json={})

        assert resp.status_code == 422

    def test_servicio_es_llamado_con_correo_correcto(self, client, mock_servicio):
        """Verifica que el servicio recibe el correo normalizado."""
        mock_servicio.solicitar_recuperacion_contrasenia = AsyncMock()

        client.post(self.URL, json={"correo": "Test@Example.COM"})

        mock_servicio.solicitar_recuperacion_contrasenia.assert_awaited_once_with(
            "test@example.com"
        )


# ═════════════════════════════════════════════════════════════════════════════
#  5. Endpoints HTTP — /api/v1/usuario/reset-password
# ═════════════════════════════════════════════════════════════════════════════

class TestResetPasswordEndpoint:
    """Pruebas de integración (TestClient) para POST /reset-password."""

    URL = "/usuario/reset-password"

    def _payload_valido(self, **overrides):
        base = {
            "token": TOKEN_VALIDO,
            "nueva_contrasenia": CONTRASENIA_SEGURA,
            "confirmar_contrasenia": CONTRASENIA_SEGURA,
        }
        base.update(overrides)
        return base

    def test_restablecimiento_exitoso_retorna_200(self, client, mock_servicio):
        """Flujo feliz: token válido y contraseña segura retorna 200."""
        mock_servicio.restablecer_contrasenia = AsyncMock()

        resp = client.post(self.URL, json=self._payload_valido())

        assert resp.status_code == 200
        assert "exitosamente" in resp.json()["mensaje"].lower()

    def test_token_invalido_retorna_401(self, client, mock_servicio):
        """Un token JWT inválido o expirado produce un 401."""
        mock_servicio.restablecer_contrasenia = AsyncMock(
            side_effect=TokenError("Token invalido o expirado")
        )

        resp = client.post(self.URL, json=self._payload_valido())

        assert resp.status_code == 401

    def test_token_expirado_retorna_401(self, client, mock_servicio):
        """Un token de recuperación ya expirado produce 401."""
        mock_servicio.restablecer_contrasenia = AsyncMock(
            side_effect=TokenError("Token invalido o expirado")
        )

        resp = client.post(self.URL, json=self._payload_valido())

        assert resp.status_code == 401

    def test_enlace_ya_usado_retorna_400(self, client, mock_servicio):
        """Un enlace ya utilizado o expirado en BD produce 400."""
        mock_servicio.restablecer_contrasenia = AsyncMock(
            side_effect=ValueError("El enlace de recuperación no es válido o ya expiró.")
        )

        resp = client.post(self.URL, json=self._payload_valido())

        assert resp.status_code == 400

    def test_contrasenia_debil_retorna_422(self, client):
        """Una contraseña que no cumple los requisitos produce 422."""
        resp = client.post(self.URL, json=self._payload_valido(
            nueva_contrasenia="debil",
            confirmar_contrasenia="debil",
        ))

        assert resp.status_code == 422

    def test_contrasenias_no_coinciden_retorna_422(self, client):
        """Si las contraseñas no coinciden, Pydantic produce 422."""
        resp = client.post(self.URL, json=self._payload_valido(
            confirmar_contrasenia="Diferente@999",
        ))

        assert resp.status_code == 422

    def test_token_vacio_retorna_422(self, client):
        """Un token vacío produce 422 de validación de esquema."""
        resp = client.post(self.URL, json=self._payload_valido(token="   "))

        assert resp.status_code == 422

    def test_cuerpo_faltante_retorna_422(self, client):
        """Sin cuerpo JSON retorna 422."""
        resp = client.post(self.URL, json={})

        assert resp.status_code == 422

    def test_servicio_recibe_token_y_nueva_contrasenia(self, client, mock_servicio):
        """Verifica que el servicio recibe los parámetros correctos."""
        mock_servicio.restablecer_contrasenia = AsyncMock()

        client.post(self.URL, json=self._payload_valido())

        mock_servicio.restablecer_contrasenia.assert_awaited_once_with(
            TOKEN_VALIDO, CONTRASENIA_SEGURA
        )
