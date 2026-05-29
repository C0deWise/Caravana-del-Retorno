from unittest.mock import AsyncMock, MagicMock

import pytest

from app.usuarios.services.usuario_servicio import UsuarioServicio, pwd_context


@pytest.fixture
def mock_repositorio():
    repositorio = MagicMock()
    repositorio.buscar_por_correo = AsyncMock()
    return repositorio


@pytest.fixture
def servicio(mock_repositorio):
    return UsuarioServicio(mock_repositorio)


@pytest.mark.asyncio
async def test_autenticar_ok(servicio, mock_repositorio):
    usuario = MagicMock(
        us_codigo=1,
        us_documento="123456",
        us_correo="user@correo.com",
        us_nombre="Ana",
        us_apellido="Lopez",
        ro_codigo=2,
        co_codigo=8,
    )
    usuario.us_contrasenia = pwd_context.hash("clave1234")
    mock_repositorio.buscar_por_correo.return_value = usuario

    resultado = await servicio.autenticar("user@correo.com", "clave1234")

    assert resultado.us_codigo == 1
    mock_repositorio.buscar_por_correo.assert_called_once_with("user@correo.com")


@pytest.mark.asyncio
async def test_autenticar_falla_credenciales(servicio, mock_repositorio):
    usuario = MagicMock(us_contrasenia=pwd_context.hash("clave1234"))
    mock_repositorio.buscar_por_correo.return_value = usuario

    with pytest.raises(ValueError, match="Credenciales inválidas"):
        await servicio.autenticar("user@correo.com", "incorrecta")
