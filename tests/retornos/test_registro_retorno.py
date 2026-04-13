from unittest.mock import AsyncMock, MagicMock
import sys
import os
from app.retornos.excepciones.registro_retorno_excepciones import RetornoEstadoFinalizado, RetornoNoExistente, UsuarioNoExistente, UsuarioSinColonia, UsuarioYaRegistrado
import pytest

from app.retornos.servicios.registro_retorno_servicio import RegistroRetornoServicio

@pytest.fixture
def mock_repositorio():
    repositorio = MagicMock()
    repositorio.crear_registro_retorno = AsyncMock()
    repositorio.obtener_registro_retorno_por_usuario_y_retorno = AsyncMock()
    return repositorio

@pytest.fixture
def mock_retorno_repositorio():
    repositorio = MagicMock()
    repositorio.get_by_codigo = AsyncMock()
    return repositorio

@pytest.fixture
def mock_usuario_servicio():
    servicio = MagicMock()
    servicio.obtener_usuario_por_id = AsyncMock()
    return servicio

@pytest.fixture
def servicio(mock_repositorio, mock_retorno_repositorio, mock_usuario_servicio):
    return RegistroRetornoServicio(mock_repositorio, mock_retorno_repositorio, mock_usuario_servicio)

@pytest.fixture
def retorno_mock():
    retorno = MagicMock()
    retorno.anio = 2026
    retorno.estado = "activo"

    return retorno

@pytest.fixture
def usuario_mock():
    usuario = MagicMock()
    usuario.us_codigo = 1
    usuario.co_codigo = 2
    return usuario

@pytest.fixture
def registro_retorno_mock():
    registro = MagicMock()
    registro.reg_codigo = 1
    registro.us_codigo = 1
    registro.re_codigo = 1
    return registro


@pytest.mark.asyncio
async def test_crear_registro_retorno_exitoso(servicio, mock_repositorio, mock_retorno_repositorio, mock_usuario_servicio, retorno_mock, usuario_mock, registro_retorno_mock):
    data = MagicMock()
    data.usuario = 1
    data.retorno = 1

    mock_retorno_repositorio.get_by_codigo.return_value = retorno_mock
    mock_usuario_servicio.obtener_usuario_por_id.return_value = usuario_mock
    mock_repositorio.obtener_registro_retorno_por_usuario_y_retorno.return_value = None
    mock_repositorio.crear_registro_retorno.return_value = registro_retorno_mock

    resultado = await servicio.crear_registro_retorno(data)

    mock_retorno_repositorio.get_by_codigo.assert_called_once_with(1)
    mock_usuario_servicio.obtener_usuario_por_id.assert_called_once_with(1)
    mock_repositorio.obtener_registro_retorno_por_usuario_y_retorno.assert_called_once_with(1, 1)
    mock_repositorio.crear_registro_retorno.assert_called_once_with(data)
    assert resultado == registro_retorno_mock

@pytest.mark.asyncio
async def test_crear_registro_retorno_retorno_no_existente(servicio, mock_repositorio, mock_retorno_repositorio, mock_usuario_servicio):
    data = MagicMock()
    data.usuario = 1
    data.retorno = 1

    mock_retorno_repositorio.get_by_codigo.return_value = None

    with pytest.raises(RetornoNoExistente) as exc_info:
        await servicio.crear_registro_retorno(data)

    assert exc_info.value.detail == "El retorno con código 1 no existe."

@pytest.mark.asyncio
async def test_crear_registro_retorno_retorno_finalizado(servicio, mock_repositorio, mock_retorno_repositorio, mock_usuario_servicio, retorno_mock):
    data = MagicMock()
    data.usuario = 1
    data.retorno = 1

    retorno_mock.estado = "finalizado"
    mock_retorno_repositorio.get_by_codigo.return_value = retorno_mock

    with pytest.raises(RetornoEstadoFinalizado) as exc_info:
        await servicio.crear_registro_retorno(data)

    assert exc_info.value.detail == "No es posible inscribir en el retorno con código 1 porque ya ha finalizado."

@pytest.mark.asyncio
async def test_crear_registro_retorno_usuario_no_existente(servicio, mock_repositorio, mock_retorno_repositorio, mock_usuario_servicio, retorno_mock):
    data = MagicMock()
    data.usuario = 1
    data.retorno = 1

    mock_retorno_repositorio.get_by_codigo.return_value = retorno_mock
    mock_usuario_servicio.obtener_usuario_por_id.return_value = None

    with pytest.raises(UsuarioNoExistente) as exc_info:
        await servicio.crear_registro_retorno(data)

    assert exc_info.value.detail == "El usuario con código 1 no existe."

@pytest.mark.asyncio
async def test_crear_registro_retorno_usuario_sin_colonia(servicio, mock_repositorio, mock_retorno_repositorio, mock_usuario_servicio, retorno_mock):
    data = MagicMock()
    data.usuario = 1
    data.retorno = 1

    usuario_mock = MagicMock()
    usuario_mock.co_codigo = None

    mock_retorno_repositorio.get_by_codigo.return_value = retorno_mock
    mock_usuario_servicio.obtener_usuario_por_id.return_value = usuario_mock

    with pytest.raises(UsuarioSinColonia) as exc_info:
        await servicio.crear_registro_retorno(data)

    assert exc_info.value.detail == "El usuario con código 1 no pertenece a ninguna colonia."

@pytest.mark.asyncio
async def test_crear_registro_retorno_usuario_ya_registrado(servicio, mock_repositorio, mock_retorno_repositorio, mock_usuario_servicio, retorno_mock, usuario_mock):
    data = MagicMock()
    data.usuario = 1
    data.retorno = 1

    mock_retorno_repositorio.get_by_codigo.return_value = retorno_mock
    mock_usuario_servicio.obtener_usuario_por_id.return_value = usuario_mock
    mock_repositorio.obtener_registro_retorno_por_usuario_y_retorno.return_value = MagicMock()

    with pytest.raises(UsuarioYaRegistrado) as exc_info:
        await servicio.crear_registro_retorno(data)

    assert exc_info.value.detail == "El usuario con código 1 ya está registrado en el retorno con código 1."
