"""
    test_solicitar_parentesco.py contiene las pruebas unitarias para el método
    solicitar_parentesco del servicio UsuarioServicio.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from app.notificaciones.services.notificacion_crear_service import NotificacionCrearService
from app.usuarios.models.parentesco import EstadoSolicitudParentesco, Parentesco, TipoParentesco
from app.usuarios.services.usuario_servicio import UsuarioServicio
from app.usuarios.schemas.parentesco_esquemas import ParentescoCrear, ParentescoRespuesta


# ─── Fixture base ────────────────────────────────────────────────────────────

@pytest.fixture
def repositorio():
    """Mock del repositorio de usuarios."""
    repo = MagicMock()
    repo.existe_usuario = AsyncMock(return_value=False)
    return repo

@pytest.fixture
def solicitud_parentesco_detallada():
    """Mock de una solicitud de parentesco detallada."""
    solicitud = MagicMock()
    solicitud.codigo_solicitante = 1
    solicitud.codigo_destinatario = 2
    solicitud.tipo_parentesco = TipoParentesco.hermano
    solicitud.estado = "pendiente"
    solicitud.destinatario = MagicMock()
    solicitud.destinatario.us_nombre = "Juan"
    solicitud.destinatario.us_apellido = "Pérez"
    return solicitud

@pytest.fixture
def repositorio_parentesco(solicitud_parentesco_detallada):
    """Mock del repositorio de parentesco."""
    repo = MagicMock()
    repo.existe_parentesco = AsyncMock(return_value=False)
    repo.existe_solicitud_parentesco = AsyncMock(return_value=False)
    repo.obtener_parentesco_por_id_detallado = AsyncMock(return_value=solicitud_parentesco_detallada)
    return repo

@pytest.fixture
def servicio_notificaciones():
    """Mock del servicio de notificaciones."""
    repo = MagicMock()
    repo.crear_notificacion = AsyncMock()
    repo.crear_notificacion_lote = AsyncMock()
    return NotificacionCrearService(repo)

@pytest.fixture
def servicio(repositorio, repositorio_parentesco, servicio_notificaciones):
    """Instancia de UsuarioServicio con repositorios mockeados."""
    usuario_servicio = UsuarioServicio(
        repositorio=repositorio,
        repositorio_parentesco=repositorio_parentesco,
        servicio_notificaciones=servicio_notificaciones,
    )
    usuario_servicio.publicador.notificar = AsyncMock()  
    return usuario_servicio


@pytest.fixture
def parentesco_crear():
    """Schema válido de solicitud de parentesco."""
    return ParentescoCrear(
        codigo_solicitante=1,
        codigo_destinatario=2,
        tipo_parentesco=TipoParentesco.hermano,
    )

@pytest.fixture
def crear_parentesco_mock(parentesco_crear):
    def _crear(estado=EstadoSolicitudParentesco.pendiente):
        """Mock de un objeto Parentesco."""
        parentesco = MagicMock()
        parentesco.codigo = 1
        parentesco.codigo_solicitante = parentesco_crear.codigo_solicitante
        parentesco.codigo_destinatario = parentesco_crear.codigo_destinatario
        parentesco.tipo_parentesco = parentesco_crear.tipo_parentesco
        parentesco.estado =estado
        return parentesco
    
    return _crear

# ─── Helper ──────────────────────────────────────────────────────────────────

def configurar_existe_usuario(repositorio, solicitante: bool, destinatario: bool):
    """
    Configura el mock de repositorio.existe_usuario para retornar valores distintos
    según el código recibido: 1 → solicitante, 2 → destinatario.
    """
    async def existe_usuario_mock(campo: str, valor) -> bool:
        if campo == "us_codigo":
            if valor == 1:
                return solicitante
            if valor == 2:
                return destinatario
        return False

    repositorio.existe_usuario = existe_usuario_mock


# ─── Casos de prueba ─────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_solicitar_parentesco_exitoso(servicio, repositorio, repositorio_parentesco, crear_parentesco_mock,parentesco_crear):
    """La solicitud se crea correctamente cuando todos los datos son válidos."""
    configurar_existe_usuario(repositorio, solicitante=True, destinatario=True)
    
    solicitud_mock = crear_parentesco_mock()
    solicitud_creada = ParentescoRespuesta(
        codigo=solicitud_mock.codigo,
        codigo_solicitante=solicitud_mock.codigo_solicitante,
        codigo_destinatario=solicitud_mock.codigo_destinatario,
        tipo_parentesco=solicitud_mock.tipo_parentesco,
        estado=EstadoSolicitudParentesco.pendiente
    )
    
    repositorio_parentesco.solicitar_parentesco = AsyncMock(return_value=solicitud_mock)
    servicio.publicador.notificar = AsyncMock()
    resultado = await servicio.solicitar_parentesco(parentesco_crear)

    assert resultado == solicitud_creada
    repositorio_parentesco.solicitar_parentesco.assert_awaited_once_with(parentesco_crear)
    servicio.publicador.notificar.assert_awaited_once()


@pytest.mark.asyncio
async def test_solicitar_parentesco_mismo_usuario(servicio):
    """Lanza ValueError cuando el solicitante y el destinatario son el mismo usuario."""
    parentesco_mismo_usuario = ParentescoCrear(
        codigo_solicitante=1,
        codigo_destinatario=1,
        tipo_parentesco=TipoParentesco.hermano,
    )

    with pytest.raises(ValueError, match="El solicitante y el destinatario no pueden ser el mismo usuario."):
        await servicio.solicitar_parentesco(parentesco_mismo_usuario)


@pytest.mark.asyncio
async def test_solicitar_parentesco_solicitante_no_existe(servicio, repositorio, parentesco_crear):
    """Lanza ValueError cuando el usuario solicitante no existe."""
    configurar_existe_usuario(repositorio, solicitante=False, destinatario=True)

    with pytest.raises(ValueError, match="El usuario solicitante no existe."):
        await servicio.solicitar_parentesco(parentesco_crear)


@pytest.mark.asyncio
async def test_solicitar_parentesco_destinatario_no_existe(servicio, repositorio, parentesco_crear):
    """Lanza ValueError cuando el usuario destinatario no existe."""
    configurar_existe_usuario(repositorio, solicitante=True, destinatario=False)

    with pytest.raises(ValueError, match="El usuario destinatario no existe."):
        await servicio.solicitar_parentesco(parentesco_crear)


@pytest.mark.asyncio
async def test_solicitar_parentesco_ya_existe_parentesco(servicio, repositorio, repositorio_parentesco, parentesco_crear):
    """Lanza ValueError cuando ya hay un parentesco establecido entre los usuarios."""
    configurar_existe_usuario(repositorio, solicitante=True, destinatario=True)
    repositorio_parentesco.existe_parentesco = AsyncMock(return_value=True)

    with pytest.raises(ValueError, match="Ya existe una relación de parentesco entre estos usuarios."):
        await servicio.solicitar_parentesco(parentesco_crear)


@pytest.mark.asyncio
async def test_solicitar_parentesco_ya_existe_solicitud(servicio, repositorio, repositorio_parentesco, parentesco_crear):
    """Lanza ValueError cuando ya hay una solicitud de parentesco pendiente entre los usuarios."""
    configurar_existe_usuario(repositorio, solicitante=True, destinatario=True)
    repositorio_parentesco.existe_solicitud_parentesco = AsyncMock(return_value=True)

    with pytest.raises(ValueError, match="Ya existe una solicitud de parentesco pendiente entre estos usuarios."):
        await servicio.solicitar_parentesco(parentesco_crear)

@pytest.mark.asyncio
async def test_aceptar_solicitud_parentesco_exitoso(servicio, repositorio_parentesco, crear_parentesco_mock):
    """Acepta una solicitud de parentesco pendiente correctamente."""
    solicitud_mock = crear_parentesco_mock()
    codigo_solicitud = solicitud_mock.codigo
    solicitud_mock_aceptada = crear_parentesco_mock(estado=EstadoSolicitudParentesco.aceptada)
    solicitud_esperada = ParentescoRespuesta(
        codigo=solicitud_mock_aceptada.codigo,
        codigo_solicitante=solicitud_mock_aceptada.codigo_solicitante,
        codigo_destinatario=solicitud_mock_aceptada.codigo_destinatario,
        tipo_parentesco=solicitud_mock_aceptada.tipo_parentesco,
        estado=solicitud_mock_aceptada.estado
    )
    repositorio_parentesco.obtener_parentesco_por_id = AsyncMock(return_value=solicitud_mock)
    repositorio_parentesco.actualizar_estado_parentesco = AsyncMock(return_value=solicitud_mock_aceptada)
    servicio.publicador.notificar = AsyncMock()
    resultado = await servicio.aceptar_solicitud_parentesco(codigo_solicitud)

    assert resultado == solicitud_esperada
    repositorio_parentesco.obtener_parentesco_por_id.assert_awaited_once_with(codigo_solicitud)
    repositorio_parentesco.actualizar_estado_parentesco.assert_awaited_once_with(codigo_solicitud, EstadoSolicitudParentesco.aceptada)
    servicio.publicador.notificar.assert_awaited_once()

@pytest.mark.asyncio
async def test_rechazar_solicitud_parentesco_exitoso(servicio, repositorio_parentesco, crear_parentesco_mock):
    """Rechaza una solicitud de parentesco pendiente correctamente."""
    solicitud_mock = crear_parentesco_mock()
    codigo_solicitud = solicitud_mock.codigo
    solicitud_mock_rechazada = crear_parentesco_mock(estado=EstadoSolicitudParentesco.rechazada)
    solicitud_esperada = ParentescoRespuesta(
        codigo=solicitud_mock_rechazada.codigo,
        codigo_solicitante=solicitud_mock_rechazada.codigo_solicitante,
        codigo_destinatario=solicitud_mock_rechazada.codigo_destinatario,
        tipo_parentesco=solicitud_mock_rechazada.tipo_parentesco,
        estado=solicitud_mock_rechazada.estado
    )
    repositorio_parentesco.obtener_parentesco_por_id = AsyncMock(return_value=solicitud_mock)
    repositorio_parentesco.actualizar_estado_parentesco = AsyncMock(return_value=solicitud_mock_rechazada)
    servicio.publicador.notificar = AsyncMock()
    resultado = await servicio.rechazar_solicitud_parentesco(codigo_solicitud)

    assert resultado == solicitud_esperada
    repositorio_parentesco.obtener_parentesco_por_id.assert_awaited_once_with(codigo_solicitud)
    repositorio_parentesco.actualizar_estado_parentesco.assert_awaited_once_with(codigo_solicitud, EstadoSolicitudParentesco.rechazada)
    servicio.publicador.notificar.assert_awaited_once()

@pytest.mark.asyncio
async def test_aceptar_solicitud_parentesco_no_existe(servicio, repositorio_parentesco):
    """Lanza ValueError al intentar aceptar una solicitud de parentesco que no existe."""
    codigo_solicitud = 999
    repositorio_parentesco.obtener_parentesco_por_id = AsyncMock(return_value=None)

    with pytest.raises(ValueError, match="La solicitud de parentesco no existe."):
        await servicio.aceptar_solicitud_parentesco(codigo_solicitud)

@pytest.mark.asyncio
async def test_rechazar_solicitud_parentesco_estado_invalido(servicio, repositorio_parentesco):
    """Lanza ValueError al intentar rechazar una solicitud de parentesco que no está en estado pendiente."""
    codigo_solicitud = 1
    solicitud_mock = MagicMock()
    solicitud_mock.estado = EstadoSolicitudParentesco.aceptada
    repositorio_parentesco.obtener_parentesco_por_id = AsyncMock(return_value=solicitud_mock)

    with pytest.raises(ValueError, match="Solo se pueden rechazar solicitudes que estén en estado pendiente."):
        await servicio.rechazar_solicitud_parentesco(codigo_solicitud)