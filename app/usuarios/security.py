"""
Utilidades de autenticacion JWT para usuarios.
"""

from datetime import datetime, timedelta, timezone
from typing import Any

from jose import JWTError, jwt

from app.core.config import get_settings

ROLE_BY_CODE = {
    1: "retornante",
    2: "lider",
    3: "administrativo",
    4: "visitante",
}


class TokenError(ValueError):
    """Error controlado para problemas de validacion de token."""


def role_name_from_code(role_code: int) -> str:
    return ROLE_BY_CODE.get(role_code, "retornante")


def _encode_token(payload: dict[str, Any], expires_delta: timedelta) -> str:
    settings = get_settings()
    now = datetime.now(timezone.utc)
    to_encode = payload.copy()
    to_encode.update(
        {
            "iat": int(now.timestamp()),
            "exp": int((now + expires_delta).timestamp()),
        }
    )
    return jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )


def create_access_token(*, user_id: int, documento: str, correo: str, role_code: int, colonia_id: int | None) -> str:
    settings = get_settings()
    role_name = role_name_from_code(role_code)
    payload = {
        "sub": str(user_id),
        "documento": documento,
        "correo": correo,
        "role_code": role_code,
        "role_name": role_name,
        "colonia_id": colonia_id,
        "token_type": "access",
    }
    expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return _encode_token(payload, expires_delta)


def create_refresh_token(*, user_id: int, role_code: int) -> str:
    settings = get_settings()
    payload = {
        "sub": str(user_id),
        "role_code": role_code,
        "role_name": role_name_from_code(role_code),
        "token_type": "refresh",
    }
    expires_delta = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    return _encode_token(payload, expires_delta)


def decode_token(token: str, *, expected_type: str) -> dict[str, Any]:
    settings = get_settings()
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
    except JWTError as exc:
        raise TokenError("Token invalido o expirado") from exc

    token_type = payload.get("token_type")
    if token_type != expected_type:
        raise TokenError("Tipo de token no permitido para este endpoint")

    if not payload.get("sub"):
        raise TokenError("El token no contiene identificador de usuario")

    return payload
