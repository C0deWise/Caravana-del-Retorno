"""
    test_eliminar_grupo_retorno.py contiene pruebas para validar la eliminación en cascada de grupos de retorno.
    Se prueba tanto el caso de error (grupo no existe) como el caso exitoso con eliminación de entidades relacionadas.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.retornos.servicios.grupo_retorno_servicio import GrupoRetornoServicio
from app.retornos.repositorios.grupo_retorno_repositorio import GrupoRetornoRepositorio
from app.retornos.repositorios.solicitud_grupo_retorno_repositorio import SolicitudGrupoRetornoRepositorio
from app.retornos.repositorios.retorno_grupo_usuario_repositorio import RetornoGrupoUsuarioRepositorio
from app.retornos.excepciones.registro_retorno_excepciones import GrupoNoEncontrado
from app.retornos.modelos.registro_retorno_grupo_modelo import RegistroRetornoGrupo


@pytest.fixture
def mock_grupo_repositorio():
    """Mock para el repositorio de grupos de retorno."""
    repo = MagicMock(spec=GrupoRetornoRepositorio)
    repo.obtener_grupo_por_id = AsyncMock()
    repo.eliminar_grupo_retorno = AsyncMock()
    return repo


@pytest.fixture
def mock_solicitudes_repositorio():
    """Mock para el repositorio de solicitudes de grupos de retorno."""
    return MagicMock(spec=SolicitudGrupoRetornoRepositorio)


@pytest.fixture
def mock_usuario_grupo_repositorio():
    """Mock para el repositorio de usuarios en grupos de retorno."""
    return MagicMock(spec=RetornoGrupoUsuarioRepositorio)


@pytest.fixture
def servicio(mock_grupo_repositorio):
    """Instancia el servicio inyectando los mocks necesarios."""
    return GrupoRetornoServicio(
        repositorio_grupos=mock_grupo_repositorio,
        repositorio_solicitudes=mock_solicitudes_repositorio,
        repositorio_usuario_grupo=mock_usuario_grupo_repositorio
    )


# ===== HELPERS =====

def crear_grupo_mock(gr_codigo=1, us_codigo_lider=10):
    """Helper para crear un mock de grupo de retorno."""
    grupo = MagicMock()
    grupo.gr_codigo = gr_codigo
    grupo.us_codigo_lider = us_codigo_lider
    return grupo


def crear_solicitud_mock(solgr_codigo=1, gr_codigo=1, us_codigo=20):
    """Helper para crear un mock de solicitud de grupo de retorno."""
    solicitud = MagicMock()
    solicitud.solgr_codigo = solgr_codigo
    solicitud.gr_codigo = gr_codigo
    solicitud.us_codigo = us_codigo
    return solicitud


def crear_usuario_grupo_mock(ugr_codigo=1, gr_codigo=1, us_codigo=20):
    """Helper para crear un mock de asociación usuario-grupo."""
    usuario_grupo = MagicMock()
    usuario_grupo.ugr_codigo = ugr_codigo
    usuario_grupo.gr_codigo = gr_codigo
    usuario_grupo.us_codigo = us_codigo
    return usuario_grupo


def crear_persona_grupo_mock(pgr_codigo=1, gr_codigo=1, pe_codigo=30):
    """Helper para crear un mock de asociación persona-grupo."""
    persona_grupo = MagicMock()
    persona_grupo.pgr_codigo = pgr_codigo
    persona_grupo.gr_codigo = gr_codigo
    persona_grupo.pe_codigo = pe_codigo
    return persona_grupo


def crear_registro_retorno_grupo_mock(regg_codigo=1, gr_codigo=1, re_codigo=100):
    """Helper para crear un mock de registro retorno-grupo."""
    registro = MagicMock(spec=RegistroRetornoGrupo)
    registro.regg_codigo = regg_codigo
    registro.cod_grupo = gr_codigo
    registro.retorno = re_codigo
    registro.num_hospedaje = 5
    registro.num_transporte = 2
    return registro


# ===== TESTS =====

@pytest.mark.asyncio
async def test_eliminar_grupo_retorno_no_existe(servicio, mock_grupo_repositorio):
    """Caso de error: Intentar eliminar un grupo de retorno que no existe (404)."""
    gr_codigo = 999
    mock_grupo_repositorio.obtener_grupo_por_id.return_value = None

    with pytest.raises(GrupoNoEncontrado):
        await servicio.eliminar_grupo_retorno(gr_codigo)

    mock_grupo_repositorio.obtener_grupo_por_id.assert_called_once_with(gr_codigo)
    mock_grupo_repositorio.eliminar_grupo_retorno.assert_not_called()


@pytest.mark.asyncio
async def test_eliminar_grupo_retorno_exitoso_con_cascada(
    servicio,
    mock_grupo_repositorio,
    mock_solicitudes_repositorio,
    mock_usuario_grupo_repositorio
):
    """
    Caso exitoso: Eliminar un grupo de retorno con sus entidades relacionadas.
    
    Setup:
    - Crear un grupo de retorno (gr_codigo=1)
    - Crear una solicitud de grupo de retorno asociada
    - Crear una asociación usuario-grupo (RetornoGrupoUsuario)
    - Crear una asociación persona-grupo (persona_grupo_retorno)
    - Crear un retorno y registrar el grupo en el retorno (RegistroRetornoGrupo)
    
    Verificar:
    - El grupo se elimina correctamente
    - Las solicitudes se eliminan en cascada
    - Las asociaciones usuario-grupo se eliminan en cascada
    - Las asociaciones persona-grupo se eliminan en cascada
    - Los registros de retorno-grupo se eliminan en cascada
    """
    gr_codigo = 1
    us_codigo_lider = 10
    us_codigo_solicitante = 20
    pe_codigo = 30
    re_codigo = 100
    
    # Setup: Crear el grupo
    grupo = crear_grupo_mock(gr_codigo=gr_codigo, us_codigo_lider=us_codigo_lider)
    
    # Setup: Crear solicitudes relacionadas
    solicitud = crear_solicitud_mock(solgr_codigo=1, gr_codigo=gr_codigo, us_codigo=us_codigo_solicitante)
    grupo.solicitudes = [solicitud]  # Simular relación
    
    # Setup: Crear asociaciones usuario-grupo
    usuario_grupo = crear_usuario_grupo_mock(ugr_codigo=1, gr_codigo=gr_codigo, us_codigo=us_codigo_solicitante)
    grupo.usuarios = [usuario_grupo]  # Simular relación
    
    # Setup: Crear asociaciones persona-grupo
    persona_grupo = crear_persona_grupo_mock(pgr_codigo=1, gr_codigo=gr_codigo, pe_codigo=pe_codigo)
    grupo.miembros = [persona_grupo]  # Simular relación
    
    # Setup: Crear registros de retorno-grupo
    registro_retorno_grupo = crear_registro_retorno_grupo_mock(regg_codigo=1, gr_codigo=gr_codigo, re_codigo=re_codigo)
    grupo.registros_retornos = [registro_retorno_grupo]  # Simular relación
    
    # Configurar los mocks
    mock_grupo_repositorio.obtener_grupo_por_id.return_value = grupo
    
    # Ejecutar la eliminación
    resultado = await servicio.eliminar_grupo_retorno(gr_codigo)
    
    # Verificaciones
    assert resultado.gr_codigo == gr_codigo
    assert resultado.mensaje == "Grupo de retorno eliminado exitosamente."
    
    # Verificar que se llamó para obtener el grupo
    mock_grupo_repositorio.obtener_grupo_por_id.assert_called_once_with(gr_codigo)
    
    # Verificar que se ejecutó la eliminación
    mock_grupo_repositorio.eliminar_grupo_retorno.assert_called_once_with(gr_codigo)
    
    # Verificar que las relaciones existen en el mock (simular que SQLAlchemy las mantiene)
    assert len(grupo.solicitudes) == 1
    assert grupo.solicitudes[0].gr_codigo == gr_codigo
    
    assert len(grupo.usuarios) == 1
    assert grupo.usuarios[0].gr_codigo == gr_codigo
    
    assert len(grupo.miembros) == 1
    assert grupo.miembros[0].gr_codigo == gr_codigo
    
    # Verificar que los registros de retorno-grupo también existen
    assert len(grupo.registros_retornos) == 1
    assert grupo.registros_retornos[0].cod_grupo == gr_codigo
    assert grupo.registros_retornos[0].retorno == re_codigo
