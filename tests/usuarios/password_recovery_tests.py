"""
    password_recovery_tests.py contiene las pruebas para los endpoints y servicio
    relacionados con la recuperación y restablecimiento de contraseña:
      - POST /api/v1/usuario/forgot-password
      - POST /api/v1/usuario/reset-password
    Cubre: validaciones de esquema Pydantic, lógica de negocio del servicio,
    utilidades de seguridad (tokens JWT) y respuestas HTTP
    (usando TestClient con dependencias mockeadas).
"""

import pytest
from datetime import datetime, timedelta, timezone
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
from app.usuarios.security import (
    TokenError,
    create_access_token,
    create_password_recovery_token,
    create_refresh_token,
    decode_token,
    role_name_from_code,
)
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
        ("Ab1!", "8 caracteres"),
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


# ─── 6. Security: creación y decodificación de tokens JWT ─────────────────────

class TestPasswordRecoveryTokenCreation:
    """Pruebas de creación y decodificación de tokens de recuperación de contraseña."""

    def test_crear_token_recuperacion_retorna_token_jti_y_expires(self):
        """create_password_recovery_token retorna una tupla (token, jti, expires_at)."""
        token, jti, expires_at = create_password_recovery_token(
            user_id=1, correo="test@example.com"
        )
        assert isinstance(token, str)
        assert len(jti) == 32  # uuid4().hex es de 32 caracteres
        assert isinstance(expires_at, datetime)
        assert expires_at > datetime.now(timezone.utc)

    def test_token_recuperacion_es_decodificable(self):
        """El token generado se puede decodificar con expected_type='recovery'."""
        token, jti, _ = create_password_recovery_token(
            user_id=5, correo="user@test.com"
        )
        payload = decode_token(token, expected_type="recovery")
        assert payload["sub"] == "5"
        assert payload["correo"] == "user@test.com"
        assert payload["token_type"] == "recovery"
        assert payload["jti"] == jti

    def test_token_recuperacion_no_es_access_token(self):
        """Un token de recuperación no se puede decodificar como access."""
        token, _, _ = create_password_recovery_token(
            user_id=1, correo="test@example.com"
        )
        with pytest.raises(TokenError, match="Tipo de token"):
            decode_token(token, expected_type="access")

    def test_token_recuperacion_no_es_refresh_token(self):
        """Un token de recuperación no se puede decodificar como refresh."""
        token, _, _ = create_password_recovery_token(
            user_id=1, correo="test@example.com"
        )
        with pytest.raises(TokenError, match="Tipo de token"):
            decode_token(token, expected_type="refresh")

    def test_token_invalido_lanza_token_error(self):
        """Un token JWT inválido produce TokenError."""
        with pytest.raises(TokenError, match="invalido"):
            decode_token("token.completamente.invalido", expected_type="recovery")

    def test_token_vacio_lanza_token_error(self):
        """Un string vacío produce TokenError."""
        with pytest.raises(TokenError):
            decode_token("", expected_type="recovery")

    def test_jti_es_unico_por_llamada(self):
        """Cada llamada a create_password_recovery_token genera un jti diferente."""
        _, jti1, _ = create_password_recovery_token(user_id=1, correo="a@test.com")
        _, jti2, _ = create_password_recovery_token(user_id=1, correo="a@test.com")
        assert jti1 != jti2


class TestAccessTokenCreation:
    """Pruebas de creación de tokens de acceso (relevantes para el flujo completo)."""

    def test_crear_access_token_retorna_string(self):
        token = create_access_token(
            user_id=1,
            documento="12345",
            correo="test@test.com",
            role_code=1,
            colonia_id=None,
        )
        assert isinstance(token, str)
        assert len(token) > 20

    def test_access_token_se_decodifica_correctamente(self):
        token = create_access_token(
            user_id=10,
            documento="99999",
            correo="admin@test.com",
            role_code=3,
            colonia_id=1,
        )
        payload = decode_token(token, expected_type="access")
        assert payload["sub"] == "10"
        assert payload["correo"] == "admin@test.com"
        assert payload["role_code"] == 3
        assert payload["colonia_id"] == 1
        assert payload["token_type"] == "access"

    def test_access_token_no_es_refresh(self):
        token = create_access_token(
            user_id=1, documento="1", correo="t@t.com", role_code=1, colonia_id=None
        )
        with pytest.raises(TokenError, match="Tipo de token"):
            decode_token(token, expected_type="refresh")


class TestRefreshTokenCreation:
    """Pruebas de creación de tokens de refresco."""

    def test_crear_refresh_token_retorna_string(self):
        token = create_refresh_token(user_id=1, role_code=1)
        assert isinstance(token, str)

    def test_refresh_token_se_decodifica(self):
        token = create_refresh_token(user_id=7, role_code=2)
        payload = decode_token(token, expected_type="refresh")
        assert payload["sub"] == "7"
        assert payload["role_code"] == 2
        assert payload["token_type"] == "refresh"


class TestRoleNameFromCode:
    """Pruebas de la función role_name_from_code."""

    @pytest.mark.parametrize("code, expected", [
        (1, "retornante"),
        (2, "lider"),
        (3, "administrativo"),
        (4, "visitante"),
    ])
    def test_codigos_conocidos(self, code, expected):
        assert role_name_from_code(code) == expected

    def test_codigo_desconocido_retorna_retornante(self):
        assert role_name_from_code(99) == "retornante"


class TestDecodeTokenEdgeCases:
    """Edge cases de decodificación de tokens."""

    def test_token_con_sub_falso_lanza_error(self):
        """Un token sin 'sub' válido produce error."""
        from app.core.config import get_settings
        settings = get_settings()
        from jose import jwt as jose_jwt

        payload = {
            "sub": "",
            "correo": "test@test.com",
            "token_type": "recovery",
            "jti": "abc123",
            "iat": int(datetime.now(timezone.utc).timestamp()),
            "exp": int((datetime.now(timezone.utc) + timedelta(hours=1)).timestamp()),
        }
        token = jose_jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
        with pytest.raises(TokenError, match="identificador"):
            decode_token(token, expected_type="recovery")

    def test_token_recovery_sin_jti_lanza_error(self):
        """Un token de recovery sin 'jti' produce error."""
        from app.core.config import get_settings
        settings = get_settings()
        from jose import jwt as jose_jwt

        payload = {
            "sub": "1",
            "correo": "test@test.com",
            "token_type": "recovery",
            "iat": int(datetime.now(timezone.utc).timestamp()),
            "exp": int((datetime.now(timezone.utc) + timedelta(hours=1)).timestamp()),
        }
        token = jose_jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
        with pytest.raises(TokenError, match="identificador de seguridad"):
            decode_token(token, expected_type="recovery")

    def test_token_firmado_con_otra_key_lanza_error(self):
        """Un token firmado con otra clave produce error."""
        from jose import jwt as jose_jwt

        payload = {
            "sub": "1",
            "correo": "test@test.com",
            "token_type": "recovery",
            "jti": "abc",
            "iat": int(datetime.now(timezone.utc).timestamp()),
            "exp": int((datetime.now(timezone.utc) + timedelta(hours=1)).timestamp()),
        }
        token = jose_jwt.encode(payload, "wrong-secret-key", algorithm="HS256")
        with pytest.raises(TokenError):
            decode_token(token, expected_type="recovery")


# ─── 7. Servicio: edge cases adicionales ──────────────────────────────────────

class TestSolicitarRecuperacionEdgeCases:
    """Edge cases adicionales para solicitar_recuperacion_contrasenia."""

    @pytest.mark.asyncio
    async def test_correo_con_espacios_se_normaliza(self, servicio, repositorio):
        """El correo con espacios extra se normaliza correctamente."""
        repositorio.buscar_por_correo = AsyncMock(return_value=None)
        await servicio.solicitar_recuperacion_contrasenia("  spaces@test.com  ")
        repositorio.buscar_por_correo.assert_awaited_once_with("spaces@test.com")

    @pytest.mark.asyncio
    async def test_varias_llamadas_secuenciales_funcionan(self, servicio, repositorio, email_service):
        """Múltiples llamadas secuenciales funcionan correctamente."""
        usuario = MagicMock()
        usuario.us_codigo = 1
        usuario.us_correo = "test@example.com"
        usuario.us_nombre = "Test"
        repositorio.buscar_por_correo = AsyncMock(return_value=usuario)

        expires_at = datetime.now(timezone.utc)
        with patch("app.usuarios.services.usuario_servicio.create_password_recovery_token") as mock_cpt, \
             patch("app.usuarios.services.usuario_servicio.get_settings") as mock_settings:
            mock_cpt.return_value = ("tok.abc", "jti_abc", expires_at)
            mock_settings.return_value = MagicMock(
                FRONTEND_URL="https://frontend.test",
                PASSWORD_RECOVERY_TOKEN_EXPIRE_MINUTES=30,
            )
            await servicio.solicitar_recuperacion_contrasenia("test@example.com")
            await servicio.solicitar_recuperacion_contrasenia("test@example.com")

        assert repositorio.revocar_tokens_recuperacion_activos.await_count == 2
        assert repositorio.crear_token_recuperacion.await_count == 2
        assert email_service.send_password_recovery_email.await_count == 2


class TestRestablecerContraseniaEdgeCases:
    """Edge cases adicionales para restablecer_contrasenia."""

    @pytest.mark.asyncio
    async def test_token_con_payload_incompleto_lanza_error(self, servicio):
        """Un token con payload incompleto (sin correo) produce error."""
        with patch("app.usuarios.services.usuario_servicio.decode_token") as mock_decode:
            mock_decode.return_value = {"sub": "1"}
            with pytest.raises((TokenError, ValueError)):
                await servicio.restablecer_contrasenia(TOKEN_VALIDO, CONTRASENIA_SEGURA)

    @pytest.mark.asyncio
    async def test_contrasenia_hash_empieza_con_bcrypt(self, servicio, repositorio):
        """La nueva contraseña se hashea con bcrypt correctamente."""
        usuario_mock = MagicMock()
        usuario_mock.us_codigo = 1
        usuario_mock.us_correo = "user@test.com"
        token_mock = MagicMock()
        repositorio.obtener_usuario_por_id = AsyncMock(return_value=usuario_mock)
        repositorio.obtener_token_recuperacion_activo = AsyncMock(return_value=token_mock)

        with patch("app.usuarios.services.usuario_servicio.decode_token") as mock_decode:
            mock_decode.return_value = {"sub": "1", "correo": "user@test.com", "jti": "jti123"}
            await servicio.restablecer_contrasenia(TOKEN_VALIDO, CONTRASENIA_SEGURA)

        args = repositorio.actualizar_contrasenia_con_token.call_args[0]
        hash_guardado = args[1]
        assert hash_guardado.startswith("$2b$")
        assert hash_guardado != CONTRASENIA_SEGURA

    @pytest.mark.asyncio
    async def test_verificar_contrasenia_funciona_con_hash_real(self, servicio):
        """verificar_contrasenia funciona con un hash real de bcrypt."""
        from app.usuarios.services.usuario_servicio import pwd_context
        hash_real = pwd_context.hash(CONTRASENIA_SEGURA)
        assert servicio.verificar_contrasenia(CONTRASENIA_SEGURA, hash_real) is True
        assert servicio.verificar_contrasenia("Wrong@123", hash_real) is False


# ─── 8. Repositorio: operaciones con tokens de recuperación ───────────────────

class TestRepositorioPasswordRecovery:
    """Pruebas de las operaciones del repositorio para tokens de recuperación."""

    @pytest.fixture
    def db_session(self):
        session = AsyncMock()
        return session

    @pytest.fixture
    def repo(self, db_session):
        from app.usuarios.repository.usuario_repositorio import UsuarioRepositorio
        return UsuarioRepositorio(db_session)

    @pytest.mark.asyncio
    async def test_crear_token_recuperacion(self, repo):
        """crear_token_recuperacion crea un token y lo retorna."""
        from app.usuarios.models.password_recovery_token import PasswordRecoveryToken

        mock_token = MagicMock(spec=PasswordRecoveryToken)
        repo.db.execute = AsyncMock()
        repo.db.add = MagicMock()
        repo.db.commit = AsyncMock()
        repo.db.refresh = AsyncMock(side_effect=lambda t: setattr(t, 'prt_codigo', 1) or t)

        result = await repo.crear_token_recuperacion(
            us_codigo=1,
            jti_hash="abc123hash",
            expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
        )
        repo.db.add.assert_called_once()
        repo.db.commit.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_revocar_tokens_recuperacion_activos(self, repo):
        """revocar_tokens_recuperacion_activos marca tokens como revocados."""
        token_mock = MagicMock()
        token_mock.prt_revocado = False
        token_mock.prt_used_at = None
        token_mock.prt_expires_at = datetime.now(timezone.utc) + timedelta(hours=1)

        result_mock = MagicMock()
        result_mock.scalars.return_value.all.return_value = [token_mock]
        repo.db.execute = AsyncMock(return_value=result_mock)
        repo.db.commit = AsyncMock()

        await repo.revocar_tokens_recuperacion_activos(us_codigo=1)

        assert token_mock.prt_revocado is True
        repo.db.commit.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_revocar_tokens_marca_used_si_expirado(self, repo):
        """Si un token está expirado, se marca como usado además de revocado."""
        token_mock = MagicMock()
        token_mock.prt_revocado = False
        token_mock.prt_used_at = None
        token_mock.prt_expires_at = datetime.now(timezone.utc) - timedelta(hours=1)

        result_mock = MagicMock()
        result_mock.scalars.return_value.all.return_value = [token_mock]
        repo.db.execute = AsyncMock(return_value=result_mock)
        repo.db.commit = AsyncMock()

        await repo.revocar_tokens_recuperacion_activos(us_codigo=1)

        assert token_mock.prt_revocado is True
        assert token_mock.prt_used_at is not None

    @pytest.mark.asyncio
    async def test_obtener_token_recuperacion_activo(self, repo):
        """obtener_token_recuperacion_activo retorna el token si existe y está activo."""
        token_mock = MagicMock()
        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = token_mock
        repo.db.execute = AsyncMock(return_value=result_mock)

        result = await repo.obtener_token_recuperacion_activo(
            us_codigo=1, jti_hash="hash123"
        )
        assert result == token_mock

    @pytest.mark.asyncio
    async def test_obtener_token_recuperacion_activo_no_existe(self, repo):
        """obtener_token_recuperacion_activo retorna None si no existe."""
        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = None
        repo.db.execute = AsyncMock(return_value=result_mock)

        result = await repo.obtener_token_recuperacion_activo(
            us_codigo=1, jti_hash="hash_inexistente"
        )
        assert result is None

    @pytest.mark.asyncio
    async def test_actualizar_contrasenia_con_token(self, repo):
        """actualizar_contrasenia_con_token actualiza la contraseña y marca el token."""
        usuario_mock = MagicMock()
        usuario_mock.us_contrasenia = "old_hash"
        token_mock = MagicMock()
        token_mock.prt_used_at = None
        token_mock.prt_revocado = False

        repo.db.commit = AsyncMock()

        await repo.actualizar_contrasenia_con_token(
            usuario=usuario_mock,
            nueva_contrasenia_hash="new_hash_abc",
            token_recuperacion=token_mock,
        )

        assert usuario_mock.us_contrasenia == "new_hash_abc"
        assert token_mock.prt_used_at is not None
        assert token_mock.prt_revocado is True
        repo.db.commit.assert_awaited_once()


# ─── 9. Esquema: validaciones adicionales ─────────────────────────────────────

class TestPasswordResetRequestEdgeCases:
    """Edge cases adicionales para el esquema PasswordResetRequest."""

    def test_token_con_espacios_se_almacena_trimmed(self):
        """El token con espacios se trimea."""
        schema = PasswordResetRequest(
            token="  token con espacios  ",
            nueva_contrasenia=CONTRASENIA_SEGURA,
            confirmar_contrasenia=CONTRASENIA_SEGURA,
        )
        assert schema.token == "token con espacios"

    @pytest.mark.parametrize("contrasenia", [
        "Abcd1234!",           # 9 chars, todos los requisitos
        "MyP@ssw0rd",          # 10 chars
        "Str0ng!Pass",         # 11 chars
        "X1y!2z@3w",           # 9 chars
    ])
    def test_contrasenias_validas_variadas(self, contrasenia):
        """Variadas contraseñas que cumplen todos los requisitos."""
        schema = PasswordResetRequest(
            token="token",
            nueva_contrasenia=contrasenia,
            confirmar_contrasenia=contrasenia,
        )
        assert schema.nueva_contrasenia == contrasenia


class TestPasswordRecoveryRequestEdgeCases:
    """Edge cases adicionales para el esquema PasswordRecoveryRequest."""

    @pytest.mark.parametrize("correo", [
        "test@test.co",
        "a@b.co",
        "user.name@domain.com",
    ])
    def test_correos_cortos_validos(self, correo):
        schema = PasswordRecoveryRequest(correo=correo)
        assert schema.correo == correo.strip().lower()

    def test_correo_normalizado_a_minusculas(self):
        schema = PasswordRecoveryRequest(correo="USER@TEST.COM")
        assert schema.correo == "user@test.com"

    def test_correo_dominio_complexo(self):
        schema = PasswordRecoveryRequest(correo="user@sub.domain.co")
        assert schema.correo == "user@sub.domain.co"
