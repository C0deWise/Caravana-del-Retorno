from unittest.mock import AsyncMock, MagicMock
import pytest

from app.colonias.excepciones.excepciones import ColoniaInactiva, ColoniaNoExistente
from app.colonias.services.colonia_services import ColoniaService
from app.colonias.models.colonia_model import ColoniaEstado

@pytest.fixture
def mock_repositorio():
    repositorio = MagicMock()
    repositorio.desactivar_colonia = AsyncMock()
    repositorio.obtener_colonia_por_id = AsyncMock()
    repositorio.tiene_miembros_colonia = AsyncMock()
    repositorio.sacar_miembros_colonia = AsyncMock()
    repositorio.activar_colonia = AsyncMock()
    return repositorio

@pytest.fixture
def mock_db():
    db = MagicMock()
    return db

@pytest.fixture
def servicio(mock_repositorio, mock_db):
    return ColoniaService(mock_repositorio, mock_db)

@pytest.fixture
def colonia_mock():
    colonia = MagicMock()
    colonia.codigo = 1
    colonia.pais = "Colombia"
    colonia.departamento = "Antioquia"
    colonia.ciudad = "Medellín"
    colonia.lider = 5 #Tiene un líder asignado
    colonia.estado = ColoniaEstado.ACTIVA
    return colonia

@pytest.mark.asyncio
async def test_toggle_estado_colonia_exitoso_sin_miembros(servicio, mock_repositorio, colonia_mock):
    """Prueba para alternar el estado de una colonia sin miembros asociados exitosa."""
    mock_repositorio.obtener_colonia_por_id.return_value = colonia_mock
    mock_repositorio.tiene_miembros_colonia.return_value = False

    colonia_inactiva = MagicMock()
    colonia_inactiva.codigo = 1
    colonia_inactiva.pais = colonia_mock.pais
    colonia_inactiva.departamento = colonia_mock.departamento
    colonia_inactiva.ciudad = colonia_mock.ciudad
    colonia_inactiva.estado = ColoniaEstado.INACTIVA
    colonia_inactiva.lider = None

    mock_repositorio.desactivar_colonia.return_value = colonia_inactiva
    colonia_desactivada = await servicio.toggle_estado_colonia(1)

    assert colonia_desactivada.codigo == colonia_mock.codigo
    assert colonia_desactivada.estado == ColoniaEstado.INACTIVA
    assert colonia_desactivada.lider is None

    mock_repositorio.obtener_colonia_por_id.return_value = colonia_inactiva
    mock_repositorio.activar_colonia.return_value = colonia_mock
    colonia_activada = await servicio.toggle_estado_colonia(1)

    assert colonia_activada.codigo == colonia_mock.codigo
    assert colonia_activada.estado == ColoniaEstado.ACTIVA

    assert mock_repositorio.obtener_colonia_por_id.await_count == 2
    mock_repositorio.activar_colonia.assert_awaited_once_with(1)
    mock_repositorio.sacar_miembros_colonia.assert_not_awaited()
    

@pytest.mark.asyncio
async def test_desactivar_colonia_con_miembros(servicio, mock_repositorio, colonia_mock):
    """Prueba para desactivar una colonia con miembros asociados exitosa."""
    mock_repositorio.obtener_colonia_por_id.return_value = colonia_mock
    mock_repositorio.tiene_miembros_colonia.return_value = True
    mock_repositorio.sacar_miembros_colonia.return_value = [1, 2, 3] #IDs de miembros asociados

    colonia_inactiva = MagicMock()
    colonia_inactiva.codigo = 1
    colonia_inactiva.pais = colonia_mock.pais
    colonia_inactiva.departamento = colonia_mock.departamento
    colonia_inactiva.ciudad = colonia_mock.ciudad
    colonia_inactiva.estado = ColoniaEstado.INACTIVA
    colonia_inactiva.lider = None
    mock_repositorio.desactivar_colonia.return_value = colonia_inactiva

    resultado = await servicio.toggle_estado_colonia(1)

    assert resultado.codigo == colonia_mock.codigo
    assert resultado.estado == ColoniaEstado.INACTIVA
    assert resultado.lider is None
    mock_repositorio.sacar_miembros_colonia.assert_awaited_once_with(1)

@pytest.mark.asyncio
async def test_desactivar_colonia_no_existente(servicio, mock_repositorio, colonia_mock):
    """Prueba para desactivar una colonia que no existe."""
    mock_repositorio.obtener_colonia_por_id.return_value = None

    with pytest.raises(ColoniaNoExistente) as exc_info:
        await servicio.toggle_estado_colonia(999)
    
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Colonia con ID 999 no encontrada."

