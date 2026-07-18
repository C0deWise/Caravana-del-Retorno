from unittest.mock import AsyncMock, MagicMock
import pytest
from datetime import date

from app.colonias.models.colonia_model import ColoniaEstado
from app.colonias.services.colonia_services import ColoniaService
from app.colonias.excepciones.excepciones import (
    UsuarioNoExistente,
    ColoniaNoExistente,
    UsuarioNoEsMiembroColonia,
    UsuarioInscritoRetornoActivo,
    AutoRemocionUsuarioColonia,
)

@pytest.fixture
def mock_repositorio_colonia():
    repositorio = MagicMock()
    repositorio.obtener_colonia_por_id = AsyncMock()
    repositorio.remover_miembro_colonia = AsyncMock()
    return repositorio

@pytest.fixture
def mock_usuario_servicio():
    servicio = MagicMock()
    servicio.obtener_usuario_por_id = AsyncMock()
    return servicio

@pytest.fixture
def mock_registro_retorno_servicio():
    servicio = MagicMock()
    servicio.obtener_registros_retorno_activos_por_usuario = AsyncMock()
    return servicio

@pytest.fixture
def servicio_colonia(mock_repositorio_colonia, mock_usuario_servicio, mock_registro_retorno_servicio):
    return ColoniaService(
        mock_repositorio_colonia,
        mock_usuario_servicio,
        mock_registro_retorno_servicio
    )

@pytest.fixture
def colonia_mock():
    """Colonia activa con líder asignado"""
    colonia = MagicMock()
    colonia.codigo = 1
    colonia.pais = "Colombia"
    colonia.departamento = "Antioquia"
    colonia.ciudad = "Medellín"
    colonia.lider = 1  # Líder diferente al usuario a remover
    colonia.estado = ColoniaEstado.ACTIVA
    return colonia

@pytest.fixture
def usuario_mock():
    """Usuario regular que es miembro de la colonia"""
    usuario = MagicMock()
    usuario.us_codigo = 2
    usuario.us_tipo_doc = "CC"
    usuario.us_documento = "1234567890"
    usuario.us_celular = "3001234567"
    usuario.us_nombre = "Juan"
    usuario.us_apellido = "Pérez"
    usuario.us_genero = "M"
    usuario.us_fecha_nacimiento = date(1990, 1, 1)
    usuario.us_pais = "Colombia"
    usuario.us_correo = "juan.perez@example.com"
    usuario.co_codigo = 1  # Miembro de colonia 1
    usuario.ro_codigo = 1  # Rol usuario regular
    return usuario

@pytest.fixture
def usuario_lider_mock():
    """Usuario que es líder de la colonia"""
    usuario = MagicMock()
    usuario.us_codigo = 1
    usuario.us_tipo_doc = "CC"
    usuario.us_documento = "9876543210"
    usuario.us_celular = "3009876543"
    usuario.us_nombre = "Ana"
    usuario.us_apellido = "García"
    usuario.us_genero = "F"
    usuario.us_fecha_nacimiento = date(1995, 5, 15)
    usuario.us_pais = "Colombia"
    usuario.us_correo = "ana.garcia@example.com"
    usuario.co_codigo = 1
    usuario.ro_codigo = 2  # Rol líder
    return usuario

@pytest.mark.asyncio
async def test_remover_miembro_exitoso(servicio_colonia,mock_repositorio_colonia,mock_usuario_servicio,
    mock_registro_retorno_servicio,colonia_mock,usuario_mock):
    """Prueba para sacar un miembro de una colonia exitosamente, validando el mensaje de respuesta y los datos del usuario removido."""
    mock_usuario_servicio.obtener_usuario_por_id.return_value = usuario_mock
    mock_repositorio_colonia.obtener_colonia_por_id.return_value = colonia_mock
    mock_registro_retorno_servicio.obtener_registros_retorno_activos_por_usuario.return_value = []
    mock_repositorio_colonia.remover_miembro_colonia.return_value = usuario_mock

    resultado = await servicio_colonia.remover_miembro_colonia(1, 2)

    call_order = [
        ('obtener_usuario_por_id', 2),
        ('obtener_colonia_por_id', 1),
        ('obtener_registros_retorno_activos_por_usuario', 2),
        ('remover_miembro_colonia', usuario_mock)
    ]

    assert resultado.mensaje == "El usuario Juan Pérez ha sido removido exitosamente de la colonia."
    assert resultado.usuario.nombre == "Juan"
    assert resultado.usuario.apellido == "Pérez"
    mock_repositorio_colonia.remover_miembro_colonia.assert_called_once_with(usuario_mock)

    assert mock_usuario_servicio.obtener_usuario_por_id.call_args.args[0] == 2
    assert mock_repositorio_colonia.obtener_colonia_por_id.call_args.args[0] == 1
    assert mock_registro_retorno_servicio.obtener_registros_retorno_activos_por_usuario.call_args.args[0] == 2

@pytest.mark.asyncio
async def test_remover_miembro_inscrito_en_retorno_activo(servicio_colonia,mock_repositorio_colonia,
    mock_usuario_servicio,mock_registro_retorno_servicio,colonia_mock,usuario_mock
):
    """
    Pruebas para sacar un miembro de una colonia que tiene registros de retorno activos, validando
    que se lance la excepción UsuarioInscritoRetornoActivo y que no se intente remover al usuario.
    """
    mock_usuario_servicio.obtener_usuario_por_id.return_value = usuario_mock
    mock_repositorio_colonia.obtener_colonia_por_id.return_value = colonia_mock
    
    retorno_activo_mock = MagicMock()
    mock_registro_retorno_servicio.obtener_registros_retorno_activos_por_usuario.return_value = [retorno_activo_mock]

    with pytest.raises(UsuarioInscritoRetornoActivo) as exc_info:
        await servicio_colonia.remover_miembro_colonia(1, 2)
    
    # Verificar que no se intentó remover
    mock_repositorio_colonia.remover_miembro_colonia.assert_not_called()

    assert exc_info.value.status_code == 409
    assert exc_info.value.detail == "El usuario con ID 2 no puede ser removido de la colonia porque esta inscrito en retornos activos."

@pytest.mark.asyncio
async def test_remover_miembro_no_pertenece_a_colonia(servicio_colonia,mock_repositorio_colonia,mock_usuario_servicio,
    colonia_mock,usuario_mock):
    """ 
    Prueba para sacar un miembro de una colonia al que el usuario no pertenece, validando que se
    lance la excepción UsuarioNoEsMiembroColonia y que no se intente remover al usuario.
    """
    usuario_mock.co_codigo = 2  # Usuario pertenece a colonia 2, no 1
    mock_usuario_servicio.obtener_usuario_por_id.return_value = usuario_mock
    mock_repositorio_colonia.obtener_colonia_por_id.return_value = colonia_mock

    # Act & Assert
    with pytest.raises(UsuarioNoEsMiembroColonia) as exc_info:
        await servicio_colonia.remover_miembro_colonia(1, 2)

    assert exc_info.value.status_code == 409
    assert exc_info.value.detail == "El usuario con ID 2 no es miembro de la colonia con ID 1."

@pytest.mark.asyncio
async def test_remover_miembro_auto_remocion(servicio_colonia,mock_repositorio_colonia,mock_usuario_servicio,
    mock_registro_retorno_servicio,colonia_mock,usuario_lider_mock):
    """
    Prueba para sacar un miembro de una colonia que es el líder, validando que se lance la excepción AutoRemocionUsuarioColonia.
    """
    colonia_mock.lider = 1  # El usuario 1 es el líder
    mock_usuario_servicio.obtener_usuario_por_id.return_value = usuario_lider_mock
    mock_repositorio_colonia.obtener_colonia_por_id.return_value = colonia_mock

    with pytest.raises(AutoRemocionUsuarioColonia) as exc_info:
        await servicio_colonia.remover_miembro_colonia(1, 1)

    assert exc_info.value.status_code == 409
    assert exc_info.value.detail == (
                "El usuario con ID 1 es el líder actual de la colonia y no puede removerse a sí mismo. "
                "Para remover al líder, primero debe asignar un nuevo líder a la colonia."
            )

@pytest.mark.asyncio
async def test_remover_miembro_usuario_no_existe(servicio_colonia,mock_usuario_servicio):
    """ Prueba para sacar un miembro de una colonia que no existe, validando que se lance la excepción UsuarioNoExistente  """
    mock_usuario_servicio.obtener_usuario_por_id.return_value = None

    with pytest.raises(UsuarioNoExistente) as exc_info:
        await servicio_colonia.remover_miembro_colonia(1, 999)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "El usuario con ID 999 no existe."

@pytest.mark.asyncio
async def test_remover_miembro_colonia_no_existe(servicio_colonia,mock_repositorio_colonia,mock_usuario_servicio,
    usuario_mock):
    """ Prueba para sacar un miembro de una colonia que no existe, validando que se lance la excepción ColoniaNoExistente  """
    mock_usuario_servicio.obtener_usuario_por_id.return_value = usuario_mock
    mock_repositorio_colonia.obtener_colonia_por_id.return_value = None

    with pytest.raises(ColoniaNoExistente) as exc_info:
        await servicio_colonia.remover_miembro_colonia(999, 2)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "La colonia con ID 999 no existe."

@pytest.mark.asyncio
async def test_actualizar_listado_tras_remocion(servicio_colonia,mock_repositorio_colonia,mock_usuario_servicio,
    mock_registro_retorno_servicio,colonia_mock,usuario_mock):
    """Prueba para verificar que después de remover un miembro de la colonia, el usuario ya no tenga un código de colonia asignado (co_codigo = None)."""

    mock_usuario_servicio.obtener_usuario_por_id.return_value = usuario_mock
    mock_repositorio_colonia.obtener_colonia_por_id.return_value = colonia_mock
    mock_registro_retorno_servicio.obtener_registros_retorno_activos_por_usuario.return_value = []
    
    usuario_removido = MagicMock()
    usuario_removido.us_codigo = usuario_mock.us_codigo
    usuario_removido.us_tipo_doc = usuario_mock.us_tipo_doc
    usuario_removido.us_documento = usuario_mock.us_documento
    usuario_removido.us_celular = usuario_mock.us_celular
    usuario_removido.us_nombre = usuario_mock.us_nombre
    usuario_removido.us_apellido = usuario_mock.us_apellido
    usuario_removido.us_genero = usuario_mock.us_genero
    usuario_removido.us_fecha_nacimiento = usuario_mock.us_fecha_nacimiento
    usuario_removido.us_pais = usuario_mock.us_pais
    usuario_removido.us_correo = usuario_mock.us_correo
    usuario_removido.co_codigo = None
    usuario_removido.ro_codigo = usuario_mock.ro_codigo
    mock_repositorio_colonia.remover_miembro_colonia.return_value = usuario_removido

    resultado = await servicio_colonia.remover_miembro_colonia(1, 2)

    assert resultado.usuario.codigo_colonia is None
    assert resultado.usuario.nombre == "Juan"
    assert resultado.usuario.apellido == "Pérez"