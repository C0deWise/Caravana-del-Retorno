from datetime import datetime

import pytest
from unittest.mock import AsyncMock, MagicMock

from app.retornos.esquemas.solicitud_grupo_retorno_esquema import SolicitudGrupoRetornoEstado
from app.retornos.esquemas.solicitud_retorno_grupo_esquema import SolicitudRetornoGrupoRespuesta
from app.retornos.excepciones.registro_retorno_excepciones import (
    SolicitudGrupoRetornoEstadoInvalido,
    SolicitudGrupoRetornoNoExistente,
    UsuarioNoPerteneceAlaMismaColonia,
)
from app.retornos.servicios.grupo_retorno_servicio import GrupoRetornoServicio


# ===========================================================================
# HELPERS
# ===========================================================================

def _make_servicio():
    """Devuelve (servicio, repo_solicitudes_mock, repo_usuario_grupo_mock)."""
    repo_solicitudes   = MagicMock()
    repo_usuario_grupo = MagicMock()
    servicio = GrupoRetornoServicio(
        repositorio_solicitudes=repo_solicitudes,
        repositorio_usuario_grupo=repo_usuario_grupo,
    )
    return servicio, repo_solicitudes, repo_usuario_grupo


def _make_solicitud(
    solgr_codigo=1,
    us_codigo=10,
    gr_codigo=20,
    us_codigo_lider=99,
    co_codigo_lider=5,
    co_codigo_usuario=5,
    estado=SolicitudGrupoRetornoEstado.PENDIENTE,
):
    """Construye un MagicMock que simula una solicitud completa."""
    lider = MagicMock()
    lider.co_codigo = co_codigo_lider

    grupo = MagicMock()
    grupo.lider = lider
    grupo.us_codigo_lider = us_codigo_lider

    usuario = MagicMock()
    usuario.co_codigo = co_codigo_usuario

    solicitud = MagicMock()
    solicitud.solgr_codigo = solgr_codigo
    solicitud.us_codigo    = us_codigo
    solicitud.gr_codigo    = gr_codigo
    solicitud.solgr_estado = estado
    solicitud.grupo        = grupo
    solicitud.usuario      = usuario
    return solicitud


def _make_solicitud_resultado(
    solgr_codigo=1,
    us_codigo=10,
    gr_codigo=20,
    estado=SolicitudGrupoRetornoEstado.ACEPTADO,
    timestamp=datetime(2024, 1, 1, 0, 0)
):
    resultado = MagicMock()
    resultado.solgr_codigo     = solgr_codigo
    resultado.us_codigo        = us_codigo
    resultado.gr_codigo        = gr_codigo
    resultado.solgr_estado     = estado
    resultado.solgr_time_stamp = timestamp
    return resultado


# ===========================================================================
# PRUEBAS: aceptar_solicitud_grupo_retorno
# ===========================================================================

@pytest.mark.asyncio
async def test_aceptar_solicitud_no_existente_lanza_excepcion():
    servicio, repo_sol, _ = _make_servicio()
    repo_sol.obtener_solicitud_por_id = AsyncMock(return_value=None)

    with pytest.raises(SolicitudGrupoRetornoNoExistente):
        await servicio.aceptar_solicitud_grupo_retorno(sol_codigo=1)

    repo_sol.obtener_solicitud_por_id.assert_awaited_once_with(1)


@pytest.mark.asyncio
async def test_aceptar_solicitud_usuario_no_pertenece_a_la_misma_colonia():
    servicio, repo_sol, _ = _make_servicio()

    solicitud = _make_solicitud(
        co_codigo_lider=5,
        co_codigo_usuario=99,   # distinto → debe fallar
    )
    repo_sol.obtener_solicitud_por_id = AsyncMock(return_value=solicitud)

    with pytest.raises(UsuarioNoPerteneceAlaMismaColonia):
        await servicio.aceptar_solicitud_grupo_retorno(sol_codigo=1)


@pytest.mark.asyncio
@pytest.mark.parametrize("estado", [
    SolicitudGrupoRetornoEstado.ACEPTADO,
    SolicitudGrupoRetornoEstado.RECHAZADO,
])
async def test_aceptar_solicitud_estado_no_pendiente_lanza_excepcion(estado):
    servicio, repo_sol, _ = _make_servicio()

    solicitud = _make_solicitud(estado=estado)
    repo_sol.obtener_solicitud_por_id = AsyncMock(return_value=solicitud)

    with pytest.raises(SolicitudGrupoRetornoEstadoInvalido):
        await servicio.aceptar_solicitud_grupo_retorno(sol_codigo=1)


@pytest.mark.asyncio
async def test_aceptar_solicitud_exitosa_retorna_respuesta():
    servicio, repo_sol, repo_ug = _make_servicio()

    solicitud        = _make_solicitud()
    solicitud_result = _make_solicitud_resultado()

    repo_sol.obtener_solicitud_por_id        = AsyncMock(return_value=solicitud)
    repo_sol.aceptar_solicitud_grupo_retorno = AsyncMock(return_value=solicitud_result)
    repo_ug.asociar_usuario_a_grupo_retorno  = AsyncMock(return_value=True)
    servicio._rechazar_solicitudes_pendientes_por_usuario = AsyncMock()

    respuesta = await servicio.aceptar_solicitud_grupo_retorno(sol_codigo=1)

    assert isinstance(respuesta, SolicitudRetornoGrupoRespuesta)
    assert respuesta.id         == solicitud_result.solgr_codigo
    assert respuesta.usuario_id == solicitud_result.us_codigo
    assert respuesta.grupo_id   == solicitud_result.gr_codigo
    assert respuesta.estado     == solicitud_result.solgr_estado
    assert respuesta.timestamp  == solicitud_result.solgr_time_stamp


@pytest.mark.asyncio
async def test_aceptar_solicitud_asociar_usuario_llamado_cuando_solicitud_aceptada():
    servicio, repo_sol, repo_ug = _make_servicio()

    solicitud        = _make_solicitud()
    solicitud_result = _make_solicitud_resultado()

    repo_sol.obtener_solicitud_por_id        = AsyncMock(return_value=solicitud)
    repo_sol.aceptar_solicitud_grupo_retorno = AsyncMock(return_value=solicitud_result)
    repo_ug.asociar_usuario_a_grupo_retorno  = AsyncMock(return_value=True)
    servicio._rechazar_solicitudes_pendientes_por_usuario = AsyncMock()

    await servicio.aceptar_solicitud_grupo_retorno(sol_codigo=1)

    repo_ug.asociar_usuario_a_grupo_retorno.assert_awaited_once_with(
        solicitud.us_codigo, solicitud.gr_codigo
    )


@pytest.mark.asyncio
async def test_aceptar_solicitud_rechazar_pendientes_siempre_llamado():
    servicio, repo_sol, repo_ug = _make_servicio()

    solicitud        = _make_solicitud()
    solicitud_result = _make_solicitud_resultado()

    repo_sol.obtener_solicitud_por_id        = AsyncMock(return_value=solicitud)
    repo_sol.aceptar_solicitud_grupo_retorno = AsyncMock(return_value=solicitud_result)
    repo_ug.asociar_usuario_a_grupo_retorno  = AsyncMock()
    servicio._rechazar_solicitudes_pendientes_por_usuario = AsyncMock()

    await servicio.aceptar_solicitud_grupo_retorno(sol_codigo=1)

    servicio._rechazar_solicitudes_pendientes_por_usuario.assert_awaited_once_with(
        solicitud.us_codigo
    )


# ===========================================================================
# PRUEBAS: rechazar_solicitud_grupo_retorno
# ===========================================================================

@pytest.mark.asyncio
async def test_rechazar_solicitud_no_existente_lanza_excepcion():
    servicio, repo_sol, _ = _make_servicio()
    repo_sol.obtener_solicitud_por_id = AsyncMock(return_value=None)

    with pytest.raises(SolicitudGrupoRetornoNoExistente):
        await servicio.rechazar_solicitud_grupo_retorno(sol_codigo=5)

    repo_sol.obtener_solicitud_por_id.assert_awaited_once_with(5)


@pytest.mark.asyncio
@pytest.mark.parametrize("estado", [
    SolicitudGrupoRetornoEstado.ACEPTADO,
    SolicitudGrupoRetornoEstado.RECHAZADO,
])
async def test_rechazar_solicitud_estado_no_pendiente_lanza_excepcion(estado):
    servicio, repo_sol, _ = _make_servicio()

    solicitud = _make_solicitud(estado=estado)
    repo_sol.obtener_solicitud_por_id = AsyncMock(return_value=solicitud)

    with pytest.raises(Exception):
        await servicio.rechazar_solicitud_grupo_retorno(sol_codigo=1)


@pytest.mark.asyncio
async def test_rechazar_solicitud_exitosa_retorna_respuesta():
    servicio, repo_sol, _ = _make_servicio()

    solicitud        = _make_solicitud()
    solicitud_result = _make_solicitud_resultado(
        estado=SolicitudGrupoRetornoEstado.RECHAZADO
    )

    repo_sol.obtener_solicitud_por_id         = AsyncMock(return_value=solicitud)
    repo_sol.rechazar_solicitud_grupo_retorno = AsyncMock(return_value=solicitud_result)

    respuesta = await servicio.rechazar_solicitud_grupo_retorno(sol_codigo=1)

    assert isinstance(respuesta, SolicitudRetornoGrupoRespuesta)
    assert respuesta.id         == solicitud_result.solgr_codigo
    assert respuesta.usuario_id == solicitud_result.us_codigo
    assert respuesta.grupo_id   == solicitud_result.gr_codigo
    assert respuesta.estado     == solicitud_result.solgr_estado
    assert respuesta.timestamp  == solicitud_result.solgr_time_stamp


@pytest.mark.asyncio
async def test_rechazar_solicitud_repositorio_llamado_con_codigo_correcto():
    servicio, repo_sol, _ = _make_servicio()

    solicitud        = _make_solicitud()
    solicitud_result = _make_solicitud_resultado(
        estado=SolicitudGrupoRetornoEstado.RECHAZADO
    )

    repo_sol.obtener_solicitud_por_id         = AsyncMock(return_value=solicitud)
    repo_sol.rechazar_solicitud_grupo_retorno = AsyncMock(return_value=solicitud_result)

    await servicio.rechazar_solicitud_grupo_retorno(sol_codigo=42)

    repo_sol.rechazar_solicitud_grupo_retorno.assert_awaited_once_with(42)