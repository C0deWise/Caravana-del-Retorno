from unittest.mock import AsyncMock, MagicMock
import pytest

from app.colonias.models.colonia_model import ColoniaEstado
from app.colonias.services.colonia_services import ColoniaService
from app.usuarios.repository.usuario_repositorio import UsuarioRepositorio
from app.usuarios.services.usuario_servicio import UsuarioServicio

@pytest.fixture
def mock_repositorio_colonia():
    repositorio = MagicMock()
    repositorio.obtener_colonia_por_id = AsyncMock()
    repositorio.cambiar_lider_colonia = AsyncMock()
    return repositorio

@pytest.fixture
def mock_repositorio_usuario():
    repositorio = MagicMock()
    repositorio.obtener_usuario_por_id = AsyncMock()
    return repositorio

@pytest.fixture
def mock_db():
    db = MagicMock()
    return db

@pytest.fixture
def servicio_colonia(mock_repositorio_colonia, mock_db):
    servicio = ColoniaService(mock_repositorio_colonia, mock_db)
    
    servicio.usuario_servicio = MagicMock()
    servicio.usuario_servicio.obtener_usuario_por_id = AsyncMock()
    return servicio

@pytest.fixture
def colonia_mock():
    colonia = MagicMock()
    colonia.codigo = 1
    colonia.pais = "Colombia"
    colonia.departamento = "Antioquia"
    colonia.ciudad = "Medellín"
    colonia.lider = 1
    colonia.estado = ColoniaEstado.ACTIVA
    return colonia

@pytest.fixture
def usuario_mock():
    usuario = MagicMock()
    usuario.us_codigo = 2
    usuario.us_tipo_doc= "CC"
    usuario.us_celular = "3001234567"
    usuario.nombre = "Juan"
    usuario.apellido = "Pérez"
    usuario.us_genero = "M"
    usuario.us_fecha_nacimiento = "1990-01-01"
    usuario.us_pais = "Colombia"
    usuario.us_correo = "juan.perez@example.com"
    usuario.us_contrasenia = "hashed_password"
    usuario.co_codigo = 1
    usuario.ro_codigo = 1
    return usuario

@pytest.mark.asyncio
async def test_cambiar_lider_colonia(servicio_colonia, mock_repositorio_colonia, colonia_mock, usuario_mock):
    mock_repositorio_colonia.obtener_colonia_por_id.return_value = colonia_mock
    servicio_colonia.usuario_servicio.obtener_usuario_por_id.return_value = usuario_mock

    colonia_actualizada = MagicMock()
    colonia_actualizada.codigo = 1
    colonia_actualizada.pais = "Colombia"
    colonia_actualizada.departamento = "Antioquia"
    colonia_actualizada.ciudad = "Medellín"
    colonia_actualizada.estado = ColoniaEstado.ACTIVA
    colonia_actualizada.lider = usuario_mock.us_codigo

    mock_repositorio_colonia.cambiar_lider_colonia.return_value = colonia_actualizada

    resultado = await servicio_colonia.cambiar_lider_colonia(colonia_mock.codigo, usuario_mock.us_codigo)

    mock_repositorio_colonia.obtener_colonia_por_id.assert_awaited_once_with(colonia_mock.codigo)
    servicio_colonia.usuario_servicio.obtener_usuario_por_id.assert_awaited_once_with(usuario_mock.us_codigo)
    mock_repositorio_colonia.cambiar_lider_colonia.assert_awaited_once_with(colonia_mock.codigo, usuario_mock.us_codigo)
    
    assert resultado.lider == usuario_mock.us_codigo

@pytest.mark.asyncio
async def test_cambiar_lider_usuario_ya_es_lider(servicio_colonia, mock_repositorio_colonia, colonia_mock, usuario_mock):
    mock_repositorio_colonia.obtener_colonia_por_id.return_value = colonia_mock
    servicio_colonia.usuario_servicio.obtener_usuario_por_id.return_value = usuario_mock

    usuario_mock.us_codigo = colonia_mock.lider

    with pytest.raises(Exception) as exc_info:
        await servicio_colonia.cambiar_lider_colonia(colonia_mock.codigo, usuario_mock.us_codigo)

    assert exc_info.value.status_code == 409
    assert exc_info.value.detail == f"El usuario con ID {usuario_mock.us_codigo} ya es líder actual de la colonia con ID {colonia_mock.codigo}."

@pytest.mark.asyncio
async def test_cambiar_lider_usuario_no_es_miembro(servicio_colonia, mock_repositorio_colonia, colonia_mock, usuario_mock):
    mock_repositorio_colonia.obtener_colonia_por_id.return_value = colonia_mock
    servicio_colonia.usuario_servicio.obtener_usuario_por_id.return_value = usuario_mock

    usuario_mock.co_codigo = 2

    with pytest.raises(Exception) as exc_info:
        await servicio_colonia.cambiar_lider_colonia(colonia_mock.codigo, usuario_mock.us_codigo)

    assert exc_info.value.status_code == 409
    assert exc_info.value.detail == f"El usuario con ID {usuario_mock.us_codigo} no es miembro de la colonia con ID {colonia_mock.codigo}."

@pytest.mark.asyncio
async def test_cambiar_lider_usuario_no_existente(servicio_colonia, mock_repositorio_colonia, colonia_mock):
    mock_repositorio_colonia.obtener_colonia_por_id.return_value = colonia_mock
    servicio_colonia.usuario_servicio.obtener_usuario_por_id.return_value = None

    with pytest.raises(Exception) as exc_info:
        await servicio_colonia.cambiar_lider_colonia(colonia_mock.codigo, 999)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == f"Usuario con ID 999 no encontrado."

@pytest.mark.asyncio
async def test_cambiar_lider_lider_ya_asignado(servicio_colonia, mock_repositorio_colonia, colonia_mock, usuario_mock):
    mock_repositorio_colonia.obtener_colonia_por_id.return_value = colonia_mock
    servicio_colonia.usuario_servicio.obtener_usuario_por_id.return_value = usuario_mock

    colonia_mock.lider = None

    with pytest.raises(Exception) as exc_info:
        await servicio_colonia.cambiar_lider_colonia(colonia_mock.codigo, usuario_mock.us_codigo)

    assert exc_info.value.status_code == 409
    assert exc_info.value.detail == f"La colonia con ID {colonia_mock.codigo} no tiene un líder asignado."

@pytest.mark.asyncio
async def test_cambiar_lider_colonia_no_existente(servicio_colonia, mock_repositorio_colonia):
    mock_repositorio_colonia.obtener_colonia_por_id.return_value = None

    with pytest.raises(Exception) as exc_info:
        await servicio_colonia.cambiar_lider_colonia(999, 1)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == f"Colonia con ID 999 no encontrada."