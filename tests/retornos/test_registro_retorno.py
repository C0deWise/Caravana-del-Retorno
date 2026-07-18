from unittest.mock import AsyncMock, MagicMock, patch
from app.retornos.excepciones.registro_retorno_excepciones import (
    RetornoNoExistente,
    RetornoEstadoInvalido,
    UsuarioNoExistente,
    UsuarioSinColonia,
    UsuarioYaRegistrado,
    UsuarioNoRegistradoEnRetorno,
    RegistroRetornoNoExistente
)
from app.retornos.excepciones.retorno_excepciones import RegistroIndividualParqueaderoExcedidoError
import pytest

from app.retornos.servicios.registro_retorno_servicio import RegistroRetornoServicio

@pytest.fixture
def mock_repositorio():
    repositorio = MagicMock()
    repositorio.crear_registro_retorno = AsyncMock()
    repositorio.obtener_registro_retorno_por_usuario_y_retorno = AsyncMock()
    repositorio.obtener_registro_retorno_por_id = AsyncMock()
    repositorio.actualizar_registro_retorno = AsyncMock()
    repositorio.eliminar_registro_retorno = AsyncMock()
    repositorio.obtener_registros_retorno_por_usuario = AsyncMock()
    repositorio.obtener_registros_retorno_activos_usuario = AsyncMock()
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
    retorno.estado = create_estado_mock("activo")
    retorno.codigo = 1
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

@pytest.fixture
def datos_registro_crear():
    datos = MagicMock()
    datos.usuario = 1
    datos.retorno = 1
    datos.num_parqueadero_carro = 0
    datos.num_parqueadero_moto = 0
    return datos

@pytest.fixture
def datos_registro_editar():
    datos = MagicMock()
    datos.num_transporte = 2
    datos.num_hospedaje = 2
    datos.num_parqueadero_carro = 0
    datos.num_parqueadero_moto = 1
    datos.anotaciones = "Actualizando registro"
    return datos

@pytest.fixture
def datos_darse_de_baja():
    datos = MagicMock()
    datos.usuario = 1
    datos.retorno = 1
    return datos

def setup_crear_registro_mocks(mock_retorno_repositorio, mock_usuario_servicio, 
                               mock_repositorio, retorno_mock, usuario_mock, 
                               ya_registrado=False):
    """Helper para configurar mocks comunes en crear_registro_retorno."""
    mock_retorno_repositorio.get_by_codigo.return_value = retorno_mock
    mock_usuario_servicio.obtener_usuario_por_id.return_value = usuario_mock
    mock_repositorio.obtener_registro_retorno_por_usuario_y_retorno.return_value = (
        MagicMock() if ya_registrado else None
    )

def create_estado_mock(valor="activo"):
    """Helper para crear un mock de Enum estado."""
    estado = MagicMock()
    estado.value = valor
    estado.__eq__ = lambda self, other: other == valor
    estado.__ne__ = lambda self, other: other != valor
    return estado

@pytest.mark.asyncio
async def test_crear_registro_retorno_exitoso(
    servicio, mock_repositorio, mock_retorno_repositorio, mock_usuario_servicio,
    retorno_mock, usuario_mock, registro_retorno_mock, datos_registro_crear
):
    """Caso de éxito: El registro se crea correctamente."""
    setup_crear_registro_mocks(mock_retorno_repositorio, mock_usuario_servicio,
                               mock_repositorio, retorno_mock, usuario_mock)
    mock_repositorio.crear_registro_retorno.return_value = registro_retorno_mock

    with patch('app.retornos.servicios.registro_retorno_servicio.RegistroRetornoRespuesta') as mock_schema:
        mock_schema.model_validate.return_value = MagicMock(reg_codigo=1)
        resultado = await servicio.crear_registro_retorno(datos_registro_crear)
        
        assert resultado.reg_codigo == 1
        mock_repositorio.crear_registro_retorno.assert_called_once_with(datos_registro_crear)

@pytest.mark.asyncio
async def test_crear_registro_retorno_no_existente(servicio, mock_retorno_repositorio, datos_registro_crear):
    """Error: El retorno especificado no existe (404)."""
    mock_retorno_repositorio.get_by_codigo.return_value = None

    with pytest.raises(RetornoNoExistente):
        await servicio.crear_registro_retorno(datos_registro_crear)

@pytest.mark.asyncio
async def test_crear_registro_retorno_finalizado(
    servicio, mock_retorno_repositorio, retorno_mock, datos_registro_crear
):
    """Error: El retorno ya ha finalizado (400)."""
    retorno_mock.estado = create_estado_mock("finalizado")
    mock_retorno_repositorio.get_by_codigo.return_value = retorno_mock

    with pytest.raises(RetornoEstadoInvalido):
        await servicio.crear_registro_retorno(datos_registro_crear)

@pytest.mark.asyncio
async def test_crear_registro_usuario_no_existente(
    servicio, mock_repositorio, mock_retorno_repositorio, mock_usuario_servicio,
    retorno_mock, datos_registro_crear
):
    """Error: El usuario especificado no existe (404)."""
    mock_retorno_repositorio.get_by_codigo.return_value = retorno_mock
    mock_usuario_servicio.obtener_usuario_por_id.return_value = None

    with pytest.raises(UsuarioNoExistente):
        await servicio.crear_registro_retorno(datos_registro_crear)

@pytest.mark.asyncio
async def test_crear_registro_usuario_sin_colonia(
    servicio, mock_repositorio, mock_retorno_repositorio, mock_usuario_servicio,
    retorno_mock, datos_registro_crear
):
    """Error: El usuario no pertenece a ninguna colonia (400)."""
    usuario_sin_colonia = MagicMock()
    usuario_sin_colonia.us_codigo = 1
    usuario_sin_colonia.co_codigo = None
    
    mock_retorno_repositorio.get_by_codigo.return_value = retorno_mock
    mock_usuario_servicio.obtener_usuario_por_id.return_value = usuario_sin_colonia

    with pytest.raises(UsuarioSinColonia):
        await servicio.crear_registro_retorno(datos_registro_crear)

@pytest.mark.asyncio
async def test_crear_registro_usuario_ya_registrado(
    servicio, mock_repositorio, mock_retorno_repositorio, mock_usuario_servicio,
    retorno_mock, usuario_mock, datos_registro_crear
):
    """Error: El usuario ya está registrado en ese retorno (409)."""
    setup_crear_registro_mocks(mock_retorno_repositorio, mock_usuario_servicio,
                               mock_repositorio, retorno_mock, usuario_mock,
                               ya_registrado=True)

    with pytest.raises(UsuarioYaRegistrado):
        await servicio.crear_registro_retorno(datos_registro_crear)

@pytest.mark.asyncio
async def test_crear_registro_parqueaderos_excedidos(
    servicio, mock_repositorio, mock_retorno_repositorio, mock_usuario_servicio,
    retorno_mock, usuario_mock, datos_registro_crear
):
    """Error: Se solicita más de 1 parqueadero para un registro individual (400)."""
    setup_crear_registro_mocks(mock_retorno_repositorio, mock_usuario_servicio,
                               mock_repositorio, retorno_mock, usuario_mock)
    
    datos_registro_crear.num_parqueadero_carro = 1
    datos_registro_crear.num_parqueadero_moto = 1

    with pytest.raises(RegistroIndividualParqueaderoExcedidoError):
        await servicio.crear_registro_retorno(datos_registro_crear)

@pytest.mark.asyncio
async def test_editar_registro_retorno_exitoso(
    servicio, mock_repositorio, mock_retorno_repositorio,
    registro_retorno_mock, retorno_mock, datos_registro_editar
):
    """Caso de éxito: El registro se edita correctamente."""
    mock_repositorio.obtener_registro_retorno_por_id.return_value = registro_retorno_mock
    mock_retorno_repositorio.get_by_codigo.return_value = retorno_mock
    mock_repositorio.actualizar_registro_retorno.return_value = None

    with patch('app.retornos.servicios.registro_retorno_servicio.RegistroRetornoRespuesta') as mock_schema:
        mock_schema.model_validate.return_value = MagicMock(reg_codigo=1)
        resultado = await servicio.editar_registro_retorno(1, datos_registro_editar)
        
        assert resultado.reg_codigo == 1
        mock_repositorio.actualizar_registro_retorno.assert_called_once_with(1, datos_registro_editar)

@pytest.mark.asyncio
async def test_editar_registro_no_existente(
    servicio, mock_repositorio, datos_registro_editar
):
    """Error: El registro a editar no existe (404)."""
    mock_repositorio.obtener_registro_retorno_por_id.return_value = None

    with pytest.raises(RegistroRetornoNoExistente):
        await servicio.editar_registro_retorno(999, datos_registro_editar)

@pytest.mark.asyncio
async def test_editar_registro_retorno_finalizado(
    servicio, mock_repositorio, mock_retorno_repositorio,
    registro_retorno_mock, retorno_mock, datos_registro_editar
):
    """Error: No se puede editar un registro de un retorno finalizado (400)."""
    retorno_mock.estado = create_estado_mock("finalizado")
    
    mock_repositorio.obtener_registro_retorno_por_id.return_value = registro_retorno_mock
    mock_retorno_repositorio.get_by_codigo.return_value = retorno_mock

    with pytest.raises(RetornoEstadoInvalido):
        await servicio.editar_registro_retorno(1, datos_registro_editar)

@pytest.mark.asyncio
async def test_obtener_registro_existente(
    servicio, mock_repositorio, registro_retorno_mock
):
    """Caso de éxito: Se obtiene un registro existente."""
    mock_repositorio.obtener_registro_retorno_por_usuario_y_retorno.return_value = registro_retorno_mock

    with patch('app.retornos.servicios.registro_retorno_servicio.RegistroRetornoRespuesta') as mock_schema:
        mock_schema.model_validate.return_value = MagicMock(reg_codigo=1)
        resultado = await servicio.obtener_registro_retorno_por_usuario_y_retorno(1, 1)
        
        assert resultado.reg_codigo == 1
        mock_repositorio.obtener_registro_retorno_por_usuario_y_retorno.assert_called_once_with(1, 1)

@pytest.mark.asyncio
async def test_obtener_registro_no_existente(servicio, mock_repositorio):
    """Caso: El registro no existe, retorna None."""
    mock_repositorio.obtener_registro_retorno_por_usuario_y_retorno.return_value = None

    resultado = await servicio.obtener_registro_retorno_por_usuario_y_retorno(1, 1)
    
    assert resultado is None