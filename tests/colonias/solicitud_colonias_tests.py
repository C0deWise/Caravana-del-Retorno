from datetime import datetime
from unittest.mock import AsyncMock, MagicMock
import sys
import os
import pytest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from app.colonias.models.solicitud_colonia import EstadoSolicitud, SolicitudColonia
from app.colonias.schemas.colonia_solicitud_schemas import SolicitudColoniaCrear
from app.colonias.services.solicitud_colonias_services import SolicitudColoniaService


@pytest.fixture
def mock_repositorio():
    repositorio = MagicMock()
    repositorio.crear_solicitud_colonia = AsyncMock()
    repositorio.expirar_pendientes = AsyncMock()
    return repositorio


@pytest.fixture
def servicio(mock_repositorio):
    return SolicitudColoniaService(mock_repositorio)


@pytest.fixture
def solicitud_mock():
    usuario = MagicMock()
    usuario.us_nombre = "Ana"
    usuario.us_apellido = "García"

    solicitud = MagicMock(spec=SolicitudColonia)
    solicitud.so_codigo = 1
    solicitud.so_estado = EstadoSolicitud.pendiente
    solicitud.so_fecha_creacion = datetime(2025, 3, 1)
    solicitud.us_codigo = 10
    solicitud.co_codigo = 20
    solicitud.usuario = usuario
    return solicitud


@pytest.mark.asyncio
async def test_crear_solicitud_llama_repositorio(servicio, mock_repositorio, solicitud_mock):
    data = SolicitudColoniaCrear(codigo_usuario=10, codigo_colonia=20)
    mock_repositorio.crear_solicitud_colonia.return_value = solicitud_mock

    resultado = await servicio.crear_solicitud(data)

    mock_repositorio.crear_solicitud_colonia.assert_called_once_with(data)
    assert resultado.codigo == solicitud_mock.so_codigo
    assert resultado.nombre_usuario == "Ana"
    assert resultado.apellido_usuario == "García"


@pytest.mark.asyncio
async def test_expirar_solicitudes_vencidas_retorna_conteo(servicio, mock_repositorio):
    mock_repositorio.expirar_pendientes.return_value = 5

    resultado = await servicio.expirar_solicitudes_vencidas()

    mock_repositorio.expirar_pendientes.assert_called_once()
    assert resultado == 5