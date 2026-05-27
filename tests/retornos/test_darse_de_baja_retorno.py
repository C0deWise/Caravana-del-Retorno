"""
    pruebas de la funcion darse de baja de un retorno de forma individual
"""

from unittest.mock import AsyncMock, MagicMock
import sys
import os
import pytest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from app.retornos.excepciones.registro_retorno_excepciones import RetornoEstadoFinalizadoDarseDeBaja, RetornoEstadoInvalido, RetornoNoExistente, UsuarioNoExistente, UsuarioNoRegistradoEnRetorno
from app.retornos.servicios.registro_retorno_servicio import RegistroRetornoServicio
from app.retornos.esquemas.retorno_esquemas import RetornoEstado

@pytest.fixture
def mock_repositorio():
    repositorio = MagicMock()
    repositorio.crear_registro_retorno = AsyncMock()
    repositorio.obtener_registro_retorno_por_usuario_y_retorno = AsyncMock()
    repositorio.eliminar_registro_retorno = AsyncMock()
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
def retorno_finalizado_mock():
    retorno = MagicMock()
    retorno.anio = 2026
    retorno.estado = RetornoEstado.FINALIZADO
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
async def test_darse_baja_retorno_exitoso(servicio, mock_repositorio, mock_retorno_repositorio, mock_usuario_servicio, retorno_mock, usuario_mock, registro_retorno_mock):
    data = MagicMock()
    data.usuario = 1
    data.retorno = 1

    mock_usuario_servicio.obtener_usuario_por_id.return_value = usuario_mock
    mock_retorno_repositorio.get_by_codigo.return_value = retorno_mock
    mock_repositorio.obtener_registro_retorno_por_usuario_y_retorno.return_value = registro_retorno_mock
    mock_repositorio.eliminar_registro_retorno.return_value = True
    resultado = await servicio.darse_de_baja(data)

    assert resultado == True

@pytest.mark.asyncio
async def test_darse_baja_retorno_usuario_no_existe(servicio, mock_repositorio, mock_retorno_repositorio, mock_usuario_servicio, retorno_mock, usuario_mock, registro_retorno_mock):
    data = MagicMock()
    data.usuario = 1
    data.retorno = 1

    mock_usuario_servicio.obtener_usuario_por_id.return_value = None
    mock_retorno_repositorio.get_by_codigo.return_value = retorno_mock
    with pytest.raises(UsuarioNoExistente) as exc_info:
        await servicio.darse_de_baja(data)

    assert exc_info.value.detail == "El usuario con código 1 no existe."

@pytest.mark.asyncio
async def test_darse_baja_retorno_usuario_no_registrado_en_retorno(servicio, mock_repositorio, mock_retorno_repositorio, mock_usuario_servicio, retorno_mock, usuario_mock, registro_retorno_mock):
    data = MagicMock()
    data.usuario = 1
    data.retorno = 1

    mock_usuario_servicio.obtener_usuario_por_id.return_value = usuario_mock
    mock_retorno_repositorio.get_by_codigo.return_value = retorno_mock
    mock_repositorio.obtener_registro_retorno_por_usuario_y_retorno.return_value = None
    with pytest.raises(UsuarioNoRegistradoEnRetorno) as exc_info:
        await servicio.darse_de_baja(data)

    assert exc_info.value.detail == "El usuario con código 1 no está registrado en el retorno con código 1."

@pytest.mark.asyncio
async def test_darse_baja_retorno_retorno_no_existe(servicio, mock_repositorio, mock_retorno_repositorio, mock_usuario_servicio, retorno_mock, usuario_mock, registro_retorno_mock):
    data = MagicMock()
    data.usuario = 1
    data.retorno = 1

    mock_usuario_servicio.obtener_usuario_por_id.return_value = usuario_mock
    mock_retorno_repositorio.get_by_codigo.return_value = None
    with pytest.raises(RetornoNoExistente) as exc_info:
        await servicio.darse_de_baja(data)
    
    assert exc_info.value.detail == "El retorno con código 1 no existe."

@pytest.mark.asyncio
async def test_darse_baja_retorno_retorno_finalizado(servicio, mock_repositorio, mock_retorno_repositorio, mock_usuario_servicio, retorno_finalizado_mock, usuario_mock, registro_retorno_mock):
    data = MagicMock()
    data.usuario = 1
    data.retorno = 1

    mock_usuario_servicio.obtener_usuario_por_id.return_value = usuario_mock
    mock_retorno_repositorio.get_by_codigo.return_value = retorno_finalizado_mock
    mock_repositorio.obtener_registro_retorno_por_usuario_y_retorno.return_value = registro_retorno_mock
    with pytest.raises(RetornoEstadoInvalido) as exc_info:
        await servicio.darse_de_baja(data)

    assert exc_info.value.detail == "No es posible darse de baja del retorno con código 1 porque su estado es 'finalizado'."