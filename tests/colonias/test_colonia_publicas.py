"""
Pruebas del servicio de colonias públicas (GET /api/v1/colonias/publicas/).
Verifican que solo se expongan colonias activas y sin datos del líder.
"""
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.colonias.models.colonia_model import ColoniaEstado
from app.colonias.services.colonia_services import ColoniaService


@pytest.fixture
def mock_repositorio():
    repositorio = MagicMock()
    repositorio.obtener_colonias_activas = AsyncMock()
    return repositorio


@pytest.fixture
def servicio(mock_repositorio):
    return ColoniaService(mock_repositorio, MagicMock())


def _colonia(codigo: int, ciudad: str | None) -> MagicMock:
    colonia = MagicMock()
    colonia.codigo = codigo
    colonia.pais = "Colombia"
    colonia.departamento = "Antioquia"
    colonia.ciudad = ciudad
    colonia.estado = ColoniaEstado.ACTIVA
    colonia.lider = 5
    return colonia


@pytest.mark.asyncio
async def test_obtener_colonias_publicas_omite_lider_y_estado(servicio, mock_repositorio):
    """Las colonias públicas no deben incluir el líder ni el estado."""
    mock_repositorio.obtener_colonias_activas.return_value = [
        _colonia(1, "Medellín"),
        _colonia(2, None),
    ]

    resultado = await servicio.obtener_colonias_publicas()

    assert [c.codigo for c in resultado] == [1, 2]
    assert resultado[0].ciudad == "Medellín"
    assert resultado[1].ciudad is None
    for colonia in resultado:
        datos = colonia.model_dump()
        assert "lider" not in datos
        assert "estado" not in datos
    mock_repositorio.obtener_colonias_activas.assert_awaited_once()


@pytest.mark.asyncio
async def test_obtener_colonias_publicas_vacio(servicio, mock_repositorio):
    """Sin colonias activas, retorna una lista vacía."""
    mock_repositorio.obtener_colonias_activas.return_value = []

    assert await servicio.obtener_colonias_publicas() == []
