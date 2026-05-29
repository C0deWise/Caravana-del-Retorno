"""
Test casos para la generación de notificaciones en operaciones de retornos.
Cubre los siguientes escenarios:
1. Darse de baja de un retorno
2. Registro de un grupo en un retorno
3. Actualización del registro de un grupo en un retorno
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch, call
from app.retornos.servicios.registro_retorno_servicio import RegistroRetornoServicio
from app.retornos.servicios.registro_retorno_grupo_servicio import RegistroRetornoGrupoServicio
from app.notificaciones.events.events import TipoEvento, EventoBase
from app.notificaciones.events.patron_observer import Publicador


# ==================== FIXTURES ====================

@pytest.fixture
def mock_repositorio_registro_retorno():
    """Mock para el repositorio de registros de retorno."""
    repositorio = MagicMock()
    repositorio.obtener_registro_retorno_por_usuario_y_retorno = AsyncMock()
    repositorio.eliminar_registro_retorno = AsyncMock()
    repositorio.obtener_registro_retorno_por_id = AsyncMock()
    repositorio.actualizar_registro_retorno = AsyncMock()
    repositorio.crear_registro_retorno = AsyncMock()
    return repositorio


@pytest.fixture
def mock_repositorio_retorno():
    """Mock para el repositorio de retornos."""
    repositorio = MagicMock()
    repositorio.get_by_codigo = AsyncMock()
    repositorio.obtener_ultimo_retorno = AsyncMock()
    return repositorio


@pytest.fixture
def mock_repositorio_grupo_retorno():
    """Mock para el repositorio de grupos de retorno."""
    repositorio = MagicMock()
    repositorio.obtener_grupo_por_id = AsyncMock()
    return repositorio


@pytest.fixture
def mock_repositorio_usuario_grupo():
    """Mock para el repositorio de usuarios en grupos de retorno."""
    repositorio = MagicMock()
    repositorio.contar_miembros_adicionales = AsyncMock()
    repositorio.obtener_miembros_por_grupo = AsyncMock()
    repositorio.asociar_usuario_a_grupo_retorno = AsyncMock()
    return repositorio


@pytest.fixture
def mock_repositorio_persona():
    """Mock para el repositorio de personas."""
    repositorio = MagicMock()
    repositorio.obtener_personas_por_grupo = AsyncMock()
    return repositorio


@pytest.fixture
def mock_repositorio_registro_grupo():
    """Mock para el repositorio de registros de grupos de retorno."""
    repositorio = MagicMock()
    repositorio.obtener_registro_por_grupo_y_retorno = AsyncMock()
    repositorio.crear_registro_grupo_retorno = AsyncMock()
    repositorio.obtener_registro_por_id = AsyncMock()
    repositorio.editar_registro_grupo_retorno = AsyncMock()
    return repositorio


@pytest.fixture
def mock_usuario_servicio():
    """Mock para el servicio de usuarios."""
    servicio = MagicMock()
    servicio.obtener_usuario_por_id = AsyncMock()
    servicio.existe_usuario = AsyncMock()
    return servicio


@pytest.fixture
def mock_servicio_notificaciones():
    """Mock para el servicio de notificaciones."""
    servicio = MagicMock()
    return servicio


@pytest.fixture
def servicio_registro_retorno(mock_repositorio_registro_retorno, mock_repositorio_retorno, 
                               mock_usuario_servicio, mock_servicio_notificaciones):
    """Crea una instancia del servicio de registro de retorno con mocks."""
    servicio = RegistroRetornoServicio(
        mock_repositorio_registro_retorno,
        mock_repositorio_retorno,
        mock_usuario_servicio
    )
    # Reemplazar el publicador con un mock si existe
    if hasattr(servicio, 'publicador'):
        servicio.publicador = MagicMock(spec=Publicador)
        servicio.publicador.notificar = AsyncMock()
    return servicio


@pytest.fixture
def servicio_registro_grupo(mock_repositorio_registro_grupo, mock_repositorio_grupo_retorno,
                            mock_repositorio_retorno, mock_repositorio_usuario_grupo,
                            mock_repositorio_persona, mock_servicio_notificaciones):
    """Crea una instancia del servicio de registro de grupo de retorno con mocks."""
    servicio = RegistroRetornoGrupoServicio(
        mock_repositorio_registro_grupo,
        mock_repositorio_grupo_retorno,
        mock_repositorio_retorno,
        mock_repositorio_usuario_grupo,
        mock_repositorio_persona,
        mock_servicio_notificaciones
    )
    # El publicador se crea automáticamente en el __init__
    servicio.publicador = MagicMock(spec=Publicador)
    servicio.publicador.notificar = AsyncMock()
    return servicio


# ==================== FIXTURES DE DATOS ====================
@pytest.fixture
def usuario_lider_mock():
    """Mock de un usuario."""
    usuario = MagicMock()
    usuario.us_codigo = 55
    usuario.us_nombre = "Carla"
    usuario.us_apellido = "Vidal"
    usuario.co_codigo = 1
    usuario.ro_codigo = 2  
    usuario.us_documento = "123456789"
    usuario.colonia = MagicMock()
    return usuario

@pytest.fixture
def colonia_mock():
    """Mock de una colonia."""
    colonia = MagicMock()
    colonia.co_codigo = 1
    colonia.co_nombre = "Colonia Ejemplo"
    colonia.lider = MagicMock()
    return colonia

@pytest.fixture
def usuario_mock():
    """Mock de un usuario."""
    usuario = MagicMock()
    usuario.us_codigo = 10
    usuario.us_nombre = "Juan"
    usuario.us_apellido = "Pérez"
    usuario.co_codigo = 1
    usuario.us_documento = "12345678"
    usuario.colonia = MagicMock()
    return usuario

@pytest.fixture
def usuario_mock():
    """Mock de un usuario."""
    usuario = MagicMock()
    usuario.us_codigo = 10
    usuario.us_nombre = "Juan"
    usuario.us_apellido = "Pérez"
    usuario.co_codigo = 1
    usuario.us_documento = "12345678"
    usuario.colonia = MagicMock()
    return usuario


@pytest.fixture
def retorno_mock():
    """Mock de un retorno activo."""
    retorno = MagicMock()
    retorno.codigo = 1
    retorno.anio = 2024
    retorno.estado = "activo"
    return retorno


@pytest.fixture
def grupo_retorno_mock():
    """Mock de un grupo de retorno."""
    grupo = MagicMock()
    grupo.gr_codigo = 5
    grupo.us_codigo_lider = 10
    return grupo


@pytest.fixture
def registro_retorno_mock(usuario_mock, retorno_mock):
    """Mock de un registro de retorno."""
    registro = MagicMock()
    registro.codigo = 1
    registro.usuario = usuario_mock.us_codigo
    registro.retorno = retorno_mock.codigo
    registro.num_hospedaje = 1
    registro.num_transporte = 1
    registro.num_parqueadero_carro = 1
    registro.num_parqueadero_moto = 0
    registro.anotacion = None
    return registro


@pytest.fixture
def registro_grupo_retorno_mock(grupo_retorno_mock, retorno_mock):
    """Mock de un registro de grupo en un retorno."""
    registro = MagicMock()
    registro.regg_codigo = 1
    registro.cod_grupo = grupo_retorno_mock.gr_codigo
    registro.retorno = retorno_mock.codigo
    registro.num_parqueadero_carro = 1
    registro.num_parqueadero_moto = 0
    registro.num_hospedaje = 2
    registro.num_transporte = 1
    registro.anotacion = None
    return registro


@pytest.fixture
def usuarios_grupo():
    """Mock de usuarios en un grupo."""
    usuario1 = MagicMock()
    usuario1.us_codigo = 10
    usuario2 = MagicMock()
    usuario2.us_codigo = 15
    return [usuario1, usuario2]


# ==================== PRUEBAS: DARSE DE BAJA RETORNO ====================

@pytest.mark.asyncio
async def test_notificacion_darse_de_baja_retorno(
    servicio_registro_retorno, mock_repositorio_registro_retorno,
    mock_repositorio_retorno, mock_usuario_servicio, usuario_mock, colonia_mock, usuario_lider_mock,retorno_mock, registro_retorno_mock
):
    """
    Test: Cuando un usuario se da de baja de un retorno,
    se genera una notificación para el usuario.
    
    Caso de uso: Usuario recibe notificación de "Te has dado de baja del retorno 2024"
    """
    # Arrange
    datos_baja = MagicMock()
    datos_baja.usuario = usuario_mock
    datos_baja.usuario.colonia = colonia_mock
    datos_baja.usuario.colonia.lider = usuario_lider_mock.us_codigo
    datos_baja.retorno = retorno_mock.codigo
    
    mock_repositorio_retorno.get_by_codigo.return_value = retorno_mock
    mock_usuario_servicio.obtener_usuario_por_id.return_value = usuario_mock
    mock_repositorio_registro_retorno.obtener_registro_retorno_por_usuario_y_retorno.return_value = registro_retorno_mock
    mock_repositorio_registro_retorno.eliminar_registro_retorno.return_value = True
    
    # Inyectar publicador
    servicio_registro_retorno.publicador = MagicMock(spec=Publicador)
    servicio_registro_retorno.publicador.notificar = AsyncMock()

    # Act
    resultado = await servicio_registro_retorno.darse_de_baja(datos_baja)

    # Assert - Verificar que se llamó al publicador
    servicio_registro_retorno.publicador.notificar.assert_called_once()
    evento = servicio_registro_retorno.publicador.notificar.call_args[1]["evento"]
    
    # Validar tipo de evento
    assert evento.tipo_evento == TipoEvento.DARSE_BAJA_RETORNO
    
    # Validar datos del evento
    assert evento.datos["retorno_anio"] == retorno_mock.anio
    assert evento.datos["usuario_nombre"] == usuario_mock.us_nombre
    assert evento.datos["usuario_apellido"] == usuario_mock.us_apellido 
    assert evento.datos["documento_usuario"] == usuario_mock.us_documento
    
    # Validar receptores (deben ser todos los miembros del grupo)
    assert evento.receptores == [usuario_lider_mock.us_codigo]





# ==================== PRUEBAS: REGISTRO GRUPO RETORNO ====================

@pytest.mark.asyncio
async def test_notificacion_registro_grupo_retorno(
    servicio_registro_grupo, mock_repositorio_grupo_retorno, mock_repositorio_retorno,
    mock_repositorio_usuario_grupo, mock_repositorio_persona, mock_repositorio_registro_grupo,
    grupo_retorno_mock, retorno_mock, usuarios_grupo
):
    """
    Test: Cuando se registra un grupo en un retorno,
    se genera una notificación para todos los miembros del grupo.
    
    Caso de uso: Todos los miembros del grupo reciben notificación de "Tu grupo ha sido registrado para el retorno 2024"
    """
    # Arrange
    datos_registro = MagicMock()
    datos_registro.cod_grupo = grupo_retorno_mock.gr_codigo
    datos_registro.retorno = retorno_mock.codigo
    datos_registro.num_parqueadero_carro = 1
    datos_registro.num_parqueadero_moto = 0
    datos_registro.num_hospedaje = 2
    datos_registro.num_transporte = 1

    mock_repositorio_grupo_retorno.obtener_grupo_por_id.return_value = grupo_retorno_mock
    mock_repositorio_retorno.obtener_ultimo_retorno.return_value = retorno_mock
    mock_repositorio_usuario_grupo.contar_miembros_adicionales.return_value = 1
    mock_repositorio_persona.obtener_personas_por_grupo.return_value = []
    mock_repositorio_registro_grupo.obtener_registro_por_grupo_y_retorno.return_value = None
    mock_repositorio_usuario_grupo.obtener_miembros_por_grupo.return_value = usuarios_grupo
    
    registro_creado = MagicMock()
    registro_creado.regg_codigo = 1
    registro_creado.cod_grupo = grupo_retorno_mock.gr_codigo
    registro_creado.retorno = retorno_mock.codigo
    registro_creado.num_parqueadero_carro = 1
    registro_creado.num_parqueadero_moto = 0
    registro_creado.num_hospedaje = 2
    registro_creado.num_transporte = 1
    registro_creado.anotacion = None
    mock_repositorio_registro_grupo.crear_registro_grupo_retorno.return_value = registro_creado
    mock_repositorio_usuario_grupo.asociar_usuario_a_grupo_retorno.return_value = None

    # Act
    resultado = await servicio_registro_grupo.crear_registro_retorno_grupo(datos_registro)

    # Assert - Verificar que se llamó al publicador
    servicio_registro_grupo.publicador.notificar.assert_called_once()
    evento = servicio_registro_grupo.publicador.notificar.call_args[1]["evento"]
    
    # Validar tipo de evento
    assert evento.tipo_evento == TipoEvento.REGISTRO_GRUPO_RETORNO
    
    # Validar datos del evento
    assert evento.datos["retorno_anio"] == retorno_mock.anio
    
    # Validar receptores (deben ser todos los miembros del grupo)
    assert evento.receptores == [usuario.us_codigo for usuario in usuarios_grupo]



# ==================== PRUEBAS: ACTUALIZACIÓN REGISTRO GRUPO ====================

@pytest.mark.asyncio
async def test_notificacion_actualizacion_registro_grupo(
    servicio_registro_grupo, mock_repositorio_grupo_retorno, mock_repositorio_retorno,
    mock_repositorio_usuario_grupo, mock_repositorio_registro_grupo,
    grupo_retorno_mock, retorno_mock, registro_grupo_retorno_mock, usuarios_grupo
):
    """
    Test: Cuando se actualiza el registro de un grupo en un retorno,
    se genera una notificación para todos los miembros del grupo.
    
    Caso de uso: Todos los miembros reciben notificación de "Tu grupo ha sido actualizado en el retorno 2024"
    """
    # Arrange
    datos_edicion = MagicMock()
    datos_edicion.num_parqueadero_carro = 2
    datos_edicion.num_parqueadero_moto = 1
    datos_edicion.num_hospedaje = 3
    datos_edicion.num_transporte = 2

    registro_actualizado = MagicMock()
    registro_actualizado.regg_codigo = 1
    registro_actualizado.cod_grupo = grupo_retorno_mock.gr_codigo
    registro_actualizado.retorno = retorno_mock.codigo
    registro_actualizado.num_parqueadero_carro = 2
    registro_actualizado.num_parqueadero_moto = 1
    registro_actualizado.num_hospedaje = 3
    registro_actualizado.num_transporte = 2
    registro_actualizado.anotacion = None

    mock_repositorio_registro_grupo.obtener_registro_por_id.return_value = registro_grupo_retorno_mock
    mock_repositorio_retorno.get_by_codigo.return_value = retorno_mock
    mock_repositorio_registro_grupo.editar_registro_grupo_retorno.return_value = registro_actualizado
    mock_repositorio_usuario_grupo.obtener_miembros_por_grupo.return_value = usuarios_grupo

    resultado = await servicio_registro_grupo.editar_registro_retorno_grupo(1, datos_edicion)

    # Assert - Verificar que se llamó al publicador
    servicio_registro_grupo.publicador.notificar.assert_called_once()
    evento = servicio_registro_grupo.publicador.notificar.call_args[1]["evento"]
    
    # Validar tipo de evento
    assert evento.tipo_evento == TipoEvento.ACTUALIZACION_REGISTRO_GRUPO
    
    # Validar datos del evento
    assert evento.datos["retorno_anio"] == retorno_mock.anio
    
    # Validar receptores (deben ser todos los miembros del grupo)
    assert evento.receptores == [usuario.us_codigo for usuario in usuarios_grupo]


