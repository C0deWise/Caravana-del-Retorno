import pytest

from app.usuarios.security import (
    TokenError,
    create_access_token,
    create_password_recovery_token,
    create_refresh_token,
    decode_token,
)


def test_create_and_decode_access_token_ok():
    token = create_access_token(
        user_id=10,
        documento="123456",
        correo="usuario@correo.com",
        role_code=2,
        colonia_id=5,
    )

    payload = decode_token(token, expected_type="access")

    assert payload["sub"] == "10"
    assert payload["role_code"] == 2
    assert payload["token_type"] == "access"


def test_refresh_token_rejected_as_access():
    refresh = create_refresh_token(user_id=15, role_code=3)

    with pytest.raises(TokenError):
        decode_token(refresh, expected_type="access")


def test_create_and_decode_password_recovery_token_ok():
    token, jti, expires_at = create_password_recovery_token(
        user_id=18,
        correo="recuperacion@correo.com",
    )

    payload = decode_token(token, expected_type="recovery")

    assert payload["sub"] == "18"
    assert payload["correo"] == "recuperacion@correo.com"
    assert payload["token_type"] == "recovery"
    assert payload["jti"] == jti
    assert expires_at is not None
