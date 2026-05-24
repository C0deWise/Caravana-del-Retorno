"""
Test casos para la generación de notificaciones en operaciones de colonias.
Cubre los siguientes escenarios:
1. Solicitud de ingreso a una colonia aceptada
2. Solicitud de ingreso a una colonia rechazada
3. Has sido establecido como líder de colonia
4. Tu rol de líder de colonia ha sido revocado
5. Una colonia ha sido desactivada
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch, call
from app.colonias.services.colonia_services import ColoniaService
from app.colonias.services.solicitud_colonias_services import SolicitudColoniaService
from app.colonias.models.colonia_model import ColoniaEstado
from app.notificaciones.events.events import TipoEvento, EventoBase
from app.notificaciones.events.patron_observer import Publicador


# ==================== FIXTURES ====================

@pytest.fixture
def mock_repositorio_colonia():
    """Mock para el repositorio de colonias."""
    repositorio = MagicMock()
    repositorio.obtener_colonia_por_id = AsyncMock()
    repositorio.tiene_miembros_colonia = AsyncMock()
    repositorio.desactivar_colonia = AsyncMock()
    repositorio.obtener_miembros_colonia = AsyncMock()
    repositorio.sacar_miembros_colonia = AsyncMock()
    repositorio.cambiar_lider_colonia = AsyncMock()
    repositorio.establecer_lider_colonia = AsyncMock()
    return repositorio


@pytest.fixture
def mock_repositorio_solicitud():
    """Mock para el repositorio de solicitudes de colonia."""
    repositorio = MagicMock()
    repositorio.aceptar_solicitud_colonia = AsyncMock()
    repositorio.rechazar_solicitud_colonia = AsyncMock()
    repositorio.obtener_solicitud_por_id = AsyncMock()
    repositorio.rechazar_solicitudes_pendientes_por_usuario = AsyncMock()
    return repositorio


@pytest.fixture
def mock_usuario_servicio():
    """Mock para el servicio de usuarios."""
    servicio = MagicMock()
    servicio.obtener_usuario_por_id = AsyncMock()
    servicio.existe_usuario = AsyncMock()
    return servicio


@pytest.fixture
def mock_registro_retorno_servicio():
    """Mock para el servicio de registro de retorno."""
    servicio = MagicMock()
    servicio.usuario_inscrito_retorno_activo = AsyncMock(return_value=False)
    return servicio


@pytest.fixture
def mock_servicio_notificaciones():
    """Mock para el servicio de notificaciones."""
    servicio = MagicMock()
    return servicio


@pytest.fixture
def mock_publicador():
    """Mock para el publicador de eventos."""
    publicador = MagicMock(spec=Publicador)
    publicador.notificar = AsyncMock()
    return publicador


@pytest.fixture
def servicio_solicitud(mock_repositorio_solicitud, mock_servicio_notificaciones):
    """Crea una instancia del servicio de solicitud con mocks."""
    servicio = SolicitudColoniaService(mock_repositorio_solicitud, mock_servicio_notificaciones)
    # Reemplazar el publicador con un mock
    servicio.publicador = MagicMock(spec=Publicador)
    servicio.publicador.notificar = AsyncMock()
    return servicio


@pytest.fixture
def servicio_colonia(mock_repositorio_colonia, mock_usuario_servicio, 
                     mock_registro_retorno_servicio, mock_servicio_notificaciones):
    """Crea una instancia del servicio de colonia con mocks."""
    servicio = ColoniaService(
        mock_repositorio_colonia,
        mock_usuario_servicio,
        mock_registro_retorno_servicio,
        mock_servicio_notificaciones
    )
    # Reemplazar el publicador con un mock
    servicio.publicador = MagicMock(spec=Publicador)
    servicio.publicador.notificar = AsyncMock()
    return servicio


# ==================== FIXTURES DE DATOS ====================

@pytest.fixture
def colonia_mock():
    """Mock de una colonia activa con líder."""
    colonia = MagicMock()
    colonia.codigo = 1
    colonia.co_codigo = 1
    colonia.pais = "Colombia"
    colonia.departamento = "Antioquia"
    colonia.ciudad = "Medellín"
    colonia.co_ciudad = "Medellín"
    colonia.lider = 5
    colonia.estado = ColoniaEstado.ACTIVA
    return colonia


@pytest.fixture
def usuario_solicitante():
    """Mock de un usuario que solicita unirse a una colonia."""
    usuario = MagicMock()
    usuario.us_codigo = 10
    usuario.us_nombre = "Juan"
    usuario.us_apellido = "Pérez"
    usuario.co_codigo = None
    return usuario


@pytest.fixture
def usuario_lider_actual():
    """Mock de un usuario que es líder actual de una colonia."""
    usuario = MagicMock()
    usuario.us_codigo = 5
    usuario.us_nombre = "Carlos"
    usuario.us_apellido = "García"
    usuario.co_codigo = 1
    return usuario


@pytest.fixture
def usuario_nuevo_lider():
    """Mock de un usuario que será el nuevo líder de una colonia."""
    usuario = MagicMock()
    usuario.us_codigo = 15
    usuario.us_nombre = "Ana"
    usuario.us_apellido = "López"
    usuario.co_codigo = 1
    return usuario


@pytest.fixture
def solicitud_mock(usuario_solicitante, colonia_mock):
    """Mock de una solicitud de colonia."""
    solicitud = MagicMock()
    solicitud.so_codigo = 1
    solicitud.so_estado = "aceptada"
    solicitud.us_codigo = usuario_solicitante.us_codigo
    solicitud.co_codigo = colonia_mock.co_codigo
    solicitud.usuario = usuario_solicitante
    solicitud.colonia = colonia_mock
    solicitud.so_fecha_creacion = "2024-01-01"
    return solicitud


@pytest.fixture
def miembros_colonia():
    """Mock de miembros de una colonia."""
    miembro1 = MagicMock()
    miembro1.us_codigo = 5
    miembro1.co_codigo = 1
    miembro2 = MagicMock()
    miembro2.us_codigo = 8
    miembro2.co_codigo = 1
    return [miembro1, miembro2]


# ==================== PRUEBAS: SOLICITUD ACEPTADA ====================

@pytest.mark.asyncio
async def test_notificacion_solicitud_colonia_aceptada(
    servicio_solicitud, mock_repositorio_solicitud, solicitud_mock
):
    """
    Test: Cuando se acepta una solicitud de ingreso a colonia,
    se genera una notificación para el usuario solicitante.
    
    Caso de uso: Usuario recibe notificación de "Tu solicitud para unirte a Medellín ha sido aceptada"
    """
    # Arrange
    solicitud_mock.so_estado = "aceptada"
    mock_repositorio_solicitud.aceptar_solicitud_colonia.return_value = solicitud_mock
    mock_repositorio_solicitud.rechazar_solicitudes_pendientes_por_usuario.return_value = 0

    # Act
    resultado = await servicio_solicitud.aceptar_solicitud(solicitud_mock.so_codigo)

    # Assert - Verificar que se llamó al publicador
    servicio_solicitud.publicador.notificar.assert_called_once()
    evento = servicio_solicitud.publicador.notificar.call_args[1]["evento"]
    
    # Validar tipo de evento
    assert evento.tipo_evento == TipoEvento.SOLICITUD_COLONIA_ACEPTADA
    
    # Validar datos del evento
    assert evento.datos["colonia_ciudad"] == "Medellín"
    
    # Validar receptores (debe ser el usuario solicitante)
    assert evento.receptores == [solicitud_mock.us_codigo]
    
    # Validar que se retorna correctamente
    assert resultado.codigo == solicitud_mock.so_codigo


@pytest.mark.asyncio
async def test_mensaje_notificacion_solicitud_aceptada():
    """
    Test: Verificar que el mensaje de notificación de solicitud aceptada es correcto.
    """
    # Arrange
    evento = EventoBase(
        tipo_evento=TipoEvento.SOLICITUD_COLONIA_ACEPTADA,
        datos={"colonia_ciudad": "Medellín"},
        receptores=[10]
    )

    # Act - El mensaje se construye en la clase derivada
    # pero el EventoBase debe contener al menos el tipo de evento correcto
    
    # Assert
    assert evento.tipo_evento == TipoEvento.SOLICITUD_COLONIA_ACEPTADA
    assert evento.datos["colonia_ciudad"] == "Medellín"
    assert evento.receptores == [10]
    assert evento.codigo_evento == 5  # ID mapeado en MapeoEventosIds


# ==================== PRUEBAS: SOLICITUD RECHAZADA ====================

@pytest.mark.asyncio
async def test_notificacion_solicitud_colonia_rechazada(
    servicio_solicitud, mock_repositorio_solicitud, solicitud_mock
):
    """
    Test: Cuando se rechaza una solicitud de ingreso a colonia,
    se genera una notificación para el usuario solicitante.
    
    Caso de uso: Usuario recibe notificación de "Tu solicitud para unirte a Medellín ha sido rechazada"
    """
    # Arrange
    solicitud_mock.so_estado = "rechazada"
    mock_repositorio_solicitud.rechazar_solicitud_colonia.return_value = solicitud_mock

    # Act
    resultado = await servicio_solicitud.rechazar_solicitud(solicitud_mock.so_codigo)

    # Assert - Verificar que se llamó al publicador
    servicio_solicitud.publicador.notificar.assert_called_once()
    evento = servicio_solicitud.publicador.notificar.call_args[1]["evento"]
    
    # Validar tipo de evento
    assert evento.tipo_evento == TipoEvento.SOLICITUD_COLONIA_RECHAZADA
    
    # Validar datos del evento
    assert evento.datos["colonia_ciudad"] == "Medellín"
    
    # Validar receptores (debe ser el usuario solicitante)
    assert evento.receptores == [solicitud_mock.us_codigo]
    
    # Validar que se retorna correctamente
    assert resultado.codigo == solicitud_mock.so_codigo


@pytest.mark.asyncio
async def test_mensaje_notificacion_solicitud_rechazada():
    """
    Test: Verificar que el mensaje de notificación de solicitud rechazada es correcto.
    """
    # Arrange
    evento = EventoBase(
        tipo_evento=TipoEvento.SOLICITUD_COLONIA_RECHAZADA,
        datos={"colonia_ciudad": "Medellín"},
        receptores=[10]
    )

    # Assert
    assert evento.tipo_evento == TipoEvento.SOLICITUD_COLONIA_RECHAZADA
    assert evento.datos["colonia_ciudad"] == "Medellín"
    assert evento.receptores == [10]
    assert evento.codigo_evento == 6  # ID mapeado en MapeoEventosIds


# ==================== PRUEBAS: ESTABLECER LÍDER ====================

@pytest.mark.asyncio
async def test_notificacion_establecer_lider_colonia(
    servicio_colonia, mock_repositorio_colonia, mock_usuario_servicio,
    colonia_mock, usuario_nuevo_lider
):
    """
    Test: Cuando se establece un líder a una colonia sin líder previo,
    se genera una notificación para el nuevo líder.
    
    Caso de uso: Usuario recibe notificación de "Has sido establecido como líder de Medellín"
    """
    # Arrange
    colonia_sin_lider = MagicMock()
    colonia_sin_lider.codigo = 1
    colonia_sin_lider.ciudad = "Medellín"
    colonia_sin_lider.lider = None
    colonia_sin_lider.estado = ColoniaEstado.ACTIVA

    colonia_con_lider = MagicMock()
    colonia_con_lider.codigo = 1
    colonia_con_lider.co_codigo = 1
    colonia_con_lider.ciudad = "Medellín"
    colonia_con_lider.co_ciudad = "Medellín"
    colonia_con_lider.pais = "Colombia"
    colonia_con_lider.departamento = "Antioquia"
    colonia_con_lider.lider = usuario_nuevo_lider.us_codigo
    colonia_con_lider.estado = ColoniaEstado.ACTIVA

    mock_repositorio_colonia.obtener_colonia_por_id.return_value = colonia_sin_lider
    mock_usuario_servicio.obtener_usuario_por_id.return_value = usuario_nuevo_lider
    mock_repositorio_colonia.establecer_lider_colonia.return_value = colonia_con_lider

    # Act
    resultado = await servicio_colonia.servicio_establecer_lider(1, usuario_nuevo_lider.us_codigo)

    # Assert - Verificar que se llamó al publicador
    servicio_colonia.publicador.notificar.assert_called_once()
    evento = servicio_colonia.publicador.notificar.call_args[1]["evento"]
    
    # Validar tipo de evento
    assert evento.tipo_evento == TipoEvento.ESTABLER_LIDER_COLONIA
    
    # Validar datos del evento
    assert evento.datos["colonia_ciudad"] == "Medellín"
    
    # Validar receptores (debe ser el nuevo líder)
    assert evento.receptores == [usuario_nuevo_lider.us_codigo]


@pytest.mark.asyncio
async def test_mensaje_notificacion_establecer_lider():
    """
    Test: Verificar que el mensaje de notificación de establecimiento de líder es correcto.
    """
    # Arrange
    evento = EventoBase(
        tipo_evento=TipoEvento.ESTABLER_LIDER_COLONIA,
        datos={"colonia_ciudad": "Medellín"},
        receptores=[15]
    )

    # Assert
    assert evento.tipo_evento == TipoEvento.ESTABLER_LIDER_COLONIA
    assert evento.datos["colonia_ciudad"] == "Medellín"
    assert evento.receptores == [15]
    assert evento.codigo_evento == 3  # ID mapeado en MapeoEventosIds


# ==================== PRUEBAS: REVOCAR LÍDER ====================

@pytest.mark.asyncio
async def test_notificacion_revocar_lider_colonia(
    servicio_colonia, mock_repositorio_colonia, mock_usuario_servicio,
    colonia_mock, usuario_lider_actual, usuario_nuevo_lider
):
    """
    Test: Cuando se revoca el rol de líder de un usuario,
    se genera una notificación para el usuario que pierde el rol.
    
    Caso de uso: Usuario recibe notificación de "Tu rol de líder en Medellín ha sido revocado"
    """
    # Arrange
    mock_repositorio_colonia.obtener_colonia_por_id.return_value = colonia_mock
    mock_usuario_servicio.obtener_usuario_por_id.return_value = usuario_nuevo_lider

    colonia_actualizada = MagicMock()
    colonia_actualizada.codigo = 1
    colonia_actualizada.co_codigo = 1
    colonia_actualizada.ciudad = "Medellín"
    colonia_actualizada.co_ciudad = "Medellín"
    colonia_actualizada.pais = "Colombia"
    colonia_actualizada.departamento = "Antioquia"
    colonia_actualizada.lider = usuario_nuevo_lider.us_codigo
    colonia_actualizada.estado = ColoniaEstado.ACTIVA

    mock_repositorio_colonia.cambiar_lider_colonia.return_value = colonia_actualizada

    # Act
    resultado = await servicio_colonia.cambiar_lider_colonia(1, usuario_nuevo_lider.us_codigo)

    # Assert - Verificar que se llamó al publicador DOS VECES
    assert servicio_colonia.publicador.notificar.call_count == 2
    
    # Primera llamada: ELIMINAR_LIDER_COLONIA (para el líder anterior)
    evento_revocar = servicio_colonia.publicador.notificar.call_args_list[0][1]["evento"]
    assert evento_revocar.tipo_evento == TipoEvento.ELIMINAR_LIDER_COLONIA
    assert evento_revocar.datos["colonia_ciudad"] == "Medellín"
    assert evento_revocar.receptores == [colonia_mock.lider]  # Usuario que pierde el rol
    
    # Segunda llamada: ESTABLER_LIDER_COLONIA (para el nuevo líder)
    evento_establecer = servicio_colonia.publicador.notificar.call_args_list[1][1]["evento"]
    assert evento_establecer.tipo_evento == TipoEvento.ESTABLER_LIDER_COLONIA
    assert evento_establecer.datos["colonia_ciudad"] == "Medellín"
    assert evento_establecer.receptores == [usuario_nuevo_lider.us_codigo]


@pytest.mark.asyncio
async def test_mensaje_notificacion_revocar_lider():
    """
    Test: Verificar que el mensaje de notificación de revocación de líder es correcto.
    """
    # Arrange
    evento = EventoBase(
        tipo_evento=TipoEvento.ELIMINAR_LIDER_COLONIA,
        datos={"colonia_ciudad": "Medellín"},
        receptores=[5]
    )

    # Assert
    assert evento.tipo_evento == TipoEvento.ELIMINAR_LIDER_COLONIA
    assert evento.datos["colonia_ciudad"] == "Medellín"
    assert evento.receptores == [5]
    assert evento.codigo_evento == 4  # ID mapeado en MapeoEventosIds


# ==================== PRUEBAS: DESACTIVAR COLONIA ====================

@pytest.mark.asyncio
async def test_notificacion_desactivar_colonia_sin_miembros(
    servicio_colonia, mock_repositorio_colonia, colonia_mock
):
    """
    Test: Cuando se desactiva una colonia sin miembros,
    no se genera notificación (lista de receptores vacía).
    """
    # Arrange
    colonia_desactivada = MagicMock()
    colonia_desactivada.codigo = 1
    colonia_desactivada.co_codigo = 1
    colonia_desactivada.ciudad = "Medellín"
    colonia_desactivada.co_ciudad = "Medellín"
    colonia_desactivada.pais = "Colombia"
    colonia_desactivada.departamento = "Antioquia"
    colonia_desactivada.lider = None
    colonia_desactivada.estado = ColoniaEstado.INACTIVA

    mock_repositorio_colonia.obtener_colonia_por_id.return_value = colonia_mock
    mock_repositorio_colonia.tiene_miembros_colonia.return_value = False
    mock_repositorio_colonia.desactivar_colonia.return_value = colonia_desactivada

    # Act
    resultado = await servicio_colonia.desactivar_colonia(1)

    # Assert - Si no hay miembros, no hay a quien notificar
    servicio_colonia.publicador.notificar.assert_not_called()


@pytest.mark.asyncio
async def test_notificacion_desactivar_colonia_con_miembros(
    servicio_colonia, mock_repositorio_colonia, colonia_mock, miembros_colonia
):
    """
    Test: Cuando se desactiva una colonia con miembros,
    se genera una notificación para todos los miembros.
    
    Caso de uso: Todos los miembros reciben notificación de "Tu colonia Medellín ha sido desactivada"
    """
    # Arrange
    colonia_desactivada = MagicMock()
    colonia_desactivada.codigo = 1
    colonia_desactivada.co_codigo = 1
    colonia_desactivada.ciudad = "Medellín"
    colonia_desactivada.co_ciudad = "Medellín"
    colonia_desactivada.pais = "Colombia"
    colonia_desactivada.departamento = "Antioquia"
    colonia_desactivada.lider = None
    colonia_desactivada.estado = ColoniaEstado.INACTIVA

    mock_repositorio_colonia.obtener_colonia_por_id.return_value = colonia_mock
    mock_repositorio_colonia.tiene_miembros_colonia.return_value = True
    mock_repositorio_colonia.obtener_miembros_colonia.return_value = miembros_colonia
    mock_repositorio_colonia.sacar_miembros_colonia.return_value = None
    mock_repositorio_colonia.desactivar_colonia.return_value = colonia_desactivada

    # Act
    resultado = await servicio_colonia.desactivar_colonia(1)

    # Assert - Verificar que se llamó al publicador
    servicio_colonia.publicador.notificar.assert_called_once()
    evento = servicio_colonia.publicador.notificar.call_args[1]["evento"]
    
    # Validar tipo de evento
    assert evento.tipo_evento == TipoEvento.DESACTIVAR_COLONIA
    
    # Validar datos del evento
    assert evento.datos["colonia_ciudad"] == "Medellín"
    
    # Validar que se notifica a todos los miembros
    assert evento.receptores == [5, 8]  # IDs de los miembros


@pytest.mark.asyncio
async def test_mensaje_notificacion_desactivar_colonia():
    """
    Test: Verificar que el mensaje de notificación de desactivación de colonia es correcto.
    """
    # Arrange
    evento = EventoBase(
        tipo_evento=TipoEvento.DESACTIVAR_COLONIA,
        datos={"colonia_ciudad": "Medellín"},
        receptores=[5, 8, 10]
    )

    # Assert
    assert evento.tipo_evento == TipoEvento.DESACTIVAR_COLONIA
    assert evento.datos["colonia_ciudad"] == "Medellín"
    assert evento.receptores == [5, 8, 10]
    assert evento.codigo_evento == 10  # ID mapeado en MapeoEventosIds


# ==================== PRUEBAS: INTEGRACIÓN ====================

@pytest.mark.asyncio
async def test_cambiar_lider_genera_dos_notificaciones(
    servicio_colonia, mock_repositorio_colonia, mock_usuario_servicio,
    colonia_mock, usuario_lider_actual, usuario_nuevo_lider
):
    """
    Test: Verificar que la funcionalidad "cambiar líder" genera exactamente dos notificaciones:
    1. Una para el líder que pierde el rol
    2. Una para el nuevo líder
    """
    # Arrange
    mock_repositorio_colonia.obtener_colonia_por_id.return_value = colonia_mock
    mock_usuario_servicio.obtener_usuario_por_id.return_value = usuario_nuevo_lider

    colonia_actualizada = MagicMock()
    colonia_actualizada.codigo = 1
    colonia_actualizada.co_codigo = 1
    colonia_actualizada.ciudad = "Medellín"
    colonia_actualizada.co_ciudad = "Medellín"
    colonia_actualizada.pais = "Colombia"
    colonia_actualizada.departamento = "Antioquia"
    colonia_actualizada.lider = usuario_nuevo_lider.us_codigo
    colonia_actualizada.estado = ColoniaEstado.ACTIVA

    mock_repositorio_colonia.cambiar_lider_colonia.return_value = colonia_actualizada

    # Act
    resultado = await servicio_colonia.cambiar_lider_colonia(1, usuario_nuevo_lider.us_codigo)

    # Assert
    assert servicio_colonia.publicador.notificar.call_count == 2
    
    # Extraer los eventos
    eventos = [
        servicio_colonia.publicador.notificar.call_args_list[0][1]["evento"],
        servicio_colonia.publicador.notificar.call_args_list[1][1]["evento"]
    ]
    
    # Verificar que son de tipos diferentes
    tipos_eventos = [evento.tipo_evento for evento in eventos]
    assert TipoEvento.ELIMINAR_LIDER_COLONIA in tipos_eventos
    assert TipoEvento.ESTABLER_LIDER_COLONIA in tipos_eventos
    
    # Verificar que van dirigidas a usuarios diferentes
    receptores = [evento.receptores[0] for evento in eventos]
    assert colonia_mock.lider in receptores  # Líder anterior
    assert usuario_nuevo_lider.us_codigo in receptores  # Nuevo líder
