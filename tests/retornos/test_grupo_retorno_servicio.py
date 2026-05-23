import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi import HTTPException, status

from app.retornos.servicios.grupo_retorno_servicio import GrupoRetornoServicio
from app.retornos.excepciones.registro_retorno_excepciones import (
    GrupoNoEncontrado,
    UsuarioNoEstaEnUnGrupo,
)
from app.retornos.esquemas.grupo_retorno_esquema import GrupoRetornoRespuesta
from app.usuarios.schemas.usuario_esquemas import UsuarioSalida


@pytest.fixture
def mocks():
    """Fixture para centralizar la creación de mocks de repositorios."""
    return {
        "retorno": MagicMock(),
        "grupos": MagicMock(),
        "solicitudes": MagicMock(),
        "usuario_grupo": MagicMock(),
        "usuario": MagicMock(),
        "registro_individual": MagicMock(),
        "registro_grupo": MagicMock()
    }

@pytest.fixture
def servicio(mocks):
    """Instancia el servicio con los mocks inyectados."""
    return GrupoRetornoServicio(
        repositorio_retorno=mocks["retorno"],
        repositorio_grupos=mocks["grupos"],
        repositorio_solicitudes=mocks["solicitudes"],
        repositorio_usuario_grupo=mocks["usuario_grupo"],
        repositorio_usuario=mocks["usuario"],
        repositorio_registro_individual=mocks["registro_individual"],
        repositorio_registro_grupo=mocks["registro_grupo"]
    )

@pytest.mark.asyncio
async def test_validar_grupo_existente_no_existe(servicio, mocks):
    """Validación: El grupo no existe."""
    mocks["grupos"].obtener_grupo_por_id = AsyncMock(return_value=None)

    with pytest.raises(GrupoNoEncontrado):
        servicio._validar_grupo_existente(999)

@pytest.mark.asyncio
async def test_validar_grupo_existente_existe(servicio, mocks):
    """Validación: El grupo existe."""
    mock_grupo = MagicMock()
    mocks["grupos"].obtener_grupo_por_id = AsyncMock(return_value=mock_grupo)

    resultado = servicio._validar_grupo_existente(1)
    assert resultado == mock_grupo

@pytest.mark.asyncio
async def test_validar_usuario_existente_no_existe(servicio, mocks):
    """Validación: El usuario no existe."""
    mocks["usuario"].obtener_usuario_por_id = AsyncMock(return_value=None)

    with pytest.raises(HTTPException) as exc:
        servicio._validar_usuario_existente(999)
    
    assert exc.value.status_code == status.HTTP_404_NOT_FOUND
    assert "no encontrado" in exc.value.detail

@pytest.mark.asyncio
async def test_validar_usuario_existente_existe(servicio, mocks):
    """Validación: El usuario existe."""
    mock_usuario = MagicMock()
    mocks["usuario"].obtener_usuario_por_id = AsyncMock(return_value=mock_usuario)

    resultado = servicio._validar_usuario_existente(1)
    assert resultado == mock_usuario

@pytest.mark.asyncio
async def test_validar_si_usuario_es_miembro_no_es_miembro(servicio, mocks):
    """Validación: El usuario no es miembro del grupo."""
    mocks["usuario_grupo"].existe_usuario_en_grupo_para_retorno = AsyncMock(return_value=False)

    with pytest.raises(UsuarioNoEstaEnUnGrupo):
        servicio._validar_si_usuario_es_miembro(1, 1)

@pytest.mark.asyncio
async def test_validar_si_usuario_es_lider_es_lider(servicio, mocks):
    """Validación: El usuario es el líder del grupo."""
    mock_grupo = MagicMock(us_codigo_lider=1)
    mocks["grupos"].obtener_grupo_por_id = AsyncMock(return_value=mock_grupo)

    with pytest.raises(HTTPException) as exc:
        servicio._validar_si_usuario_es_lider(1, 1)
    
    assert exc.value.status_code == status.HTTP_400_BAD_REQUEST
    assert "líder del grupo no puede ser removido" in exc.value.detail

@pytest.mark.asyncio
async def test_validar_si_usuario_es_lider_no_es_lider(servicio, mocks):
    """Validación: El usuario no es el líder."""
    mock_grupo = MagicMock(us_codigo_lider=99)
    mocks["grupos"].obtener_grupo_por_id = AsyncMock(return_value=mock_grupo)

    # No debería lanzar excepción
    servicio._validar_si_usuario_es_lider(1, 1)

@pytest.mark.asyncio
async def test_obtener_grupos_por_lider_id_usuario_no_existe(servicio, mocks):
    """El usuario líder no existe."""
    mocks["usuario"].obtener_usuario_por_id = AsyncMock(return_value=None)

    with pytest.raises(HTTPException) as exc:
        await servicio.obtener_grupos_por_lider_id(999)
    
    assert exc.value.status_code == status.HTTP_404_NOT_FOUND

@pytest.mark.asyncio
async def test_obtener_grupos_por_lider_id_exito(servicio, mocks):
    """Caso de éxito: Se obtienen los grupos del líder."""
    mock_usuario = MagicMock()
    mock_grupo1 = MagicMock(gr_codigo=1)
    mock_grupo2 = MagicMock(gr_codigo=2)
    
    mocks["usuario"].obtener_usuario_por_id = AsyncMock(return_value=mock_usuario)
    mocks["grupos"].obtener_grupos_por_lider_id = AsyncMock(return_value=[mock_grupo1, mock_grupo2])

    resultado = await servicio.obtener_grupos_por_lider_id(1)

    assert len(resultado) == 2
    assert isinstance(resultado[0], GrupoRetornoRespuesta)
    mocks["grupos"].obtener_grupos_por_lider_id.assert_awaited_once_with(1)

@pytest.mark.asyncio
async def test_obtener_lider_por_grupo_id_no_existe(servicio, mocks):
    """El grupo no tiene líder o no existe."""
    mocks["grupos"].obtener_lider_por_grupo_id = AsyncMock(return_value=None)

    with pytest.raises(HTTPException) as exc:
        await servicio.obtener_lider_por_grupo_id(999)
    
    assert exc.value.status_code == status.HTTP_404_NOT_FOUND
    assert "no encontrado" in exc.value.detail

@pytest.mark.asyncio
async def test_obtener_lider_por_grupo_id_exito(servicio, mocks):
    """Caso de éxito: Se obtiene el líder del grupo."""
    mock_lider = MagicMock()
    mocks["grupos"].obtener_lider_por_grupo_id = AsyncMock(return_value=mock_lider)

    resultado = await servicio.obtener_lider_por_grupo_id(1)

    assert isinstance(resultado, UsuarioSalida)
    mocks["grupos"].obtener_lider_por_grupo_id.assert_awaited_once_with(1)

@pytest.mark.asyncio
async def test_existe_grupo_retorno_no_existe(servicio, mocks):
    """El grupo no existe."""
    mocks["grupos"].obtener_grupo_por_id = AsyncMock(return_value=None)

    resultado = await servicio.existe_grupo_retorno(999)

    assert resultado is False


@pytest.mark.asyncio
async def test_existe_grupo_retorno_existe(servicio, mocks):
    """El grupo existe."""
    mocks["grupos"].obtener_grupo_por_id = AsyncMock(return_value=MagicMock())

    resultado = await servicio.existe_grupo_retorno(1)

    assert resultado is True

@pytest.mark.asyncio
async def test_remover_miembro_grupo_no_existe(servicio, mocks):
    """Error: El grupo no existe."""
    mocks["grupos"].obtener_grupo_por_id = AsyncMock(return_value=None)

    with pytest.raises(GrupoNoEncontrado):
        await servicio.remover_miembro_de_grupo_retorno(1, 999)

@pytest.mark.asyncio
async def test_remover_miembro_usuario_no_existe(servicio, mocks):
    """Error: El usuario no existe."""
    mocks["grupos"].obtener_grupo_por_id = AsyncMock(return_value=MagicMock())
    mocks["usuario"].obtener_usuario_por_id = AsyncMock(return_value=None)

    with pytest.raises(HTTPException) as exc:
        await servicio.remover_miembro_de_grupo_retorno(999, 1)
    
    assert exc.value.status_code == status.HTTP_404_NOT_FOUND

@pytest.mark.asyncio
async def test_remover_miembro_usuario_no_es_miembro(servicio, mocks):
    """Error: El usuario no es miembro del grupo."""
    mocks["grupos"].obtener_grupo_por_id = AsyncMock(return_value=MagicMock())
    mocks["usuario"].obtener_usuario_por_id = AsyncMock(return_value=MagicMock())
    mocks["usuario_grupo"].existe_usuario_en_grupo_para_retorno = AsyncMock(return_value=False)

    with pytest.raises(UsuarioNoEstaEnUnGrupo):
        await servicio.remover_miembro_de_grupo_retorno(1, 1)

@pytest.mark.asyncio
async def test_remover_miembro_es_lider(servicio, mocks):
    """Error: No se puede remover al líder."""
    mock_grupo = MagicMock(us_codigo_lider=1)
    mocks["grupos"].obtener_grupo_por_id = AsyncMock(return_value=mock_grupo)
    mocks["usuario"].obtener_usuario_por_id = AsyncMock(return_value=MagicMock())
    mocks["usuario_grupo"].existe_usuario_en_grupo_para_retorno = AsyncMock(return_value=True)

    with pytest.raises(HTTPException) as exc:
        await servicio.remover_miembro_de_grupo_retorno(1, 1)
    
    assert exc.value.status_code == status.HTTP_400_BAD_REQUEST
    assert "líder del grupo no puede ser removido" in exc.value.detail

@pytest.mark.asyncio
async def test_remover_miembro_exitoso(servicio, mocks):
    """Caso de éxito: Se remueve al miembro del grupo."""
    mock_grupo = MagicMock(us_codigo_lider=99)
    mocks["grupos"].obtener_grupo_por_id = AsyncMock(return_value=mock_grupo)
    mocks["usuario"].obtener_usuario_por_id = AsyncMock(return_value=MagicMock())
    mocks["usuario_grupo"].existe_usuario_en_grupo_para_retorno = AsyncMock(return_value=True)
    mocks["usuario_grupo"].remover_miembro_de_grupo_retorno = AsyncMock(return_value=True)

    resultado = await servicio.remover_miembro_de_grupo_retorno(1, 1)

    assert resultado is True
    mocks["usuario_grupo"].remover_miembro_de_grupo_retorno.assert_awaited_once_with(1, 1)

@pytest.mark.asyncio
async def test_obtener_usuarios_por_grupo_no_existe(servicio, mocks):
    """El grupo no existe."""
    mocks["grupos"].obtener_grupo_por_id = AsyncMock(return_value=None)

    with pytest.raises(GrupoNoEncontrado):
        await servicio.obtener_usuarios_por_grupo(999)

@pytest.mark.asyncio
async def test_obtener_usuarios_por_grupo_exito(servicio, mocks):
    """Caso de éxito: Se obtienen los usuarios del grupo."""
    mock_grupo = MagicMock()
    mock_usuario1 = MagicMock(us_codigo=1)
    mock_usuario2 = MagicMock(us_codigo=2)
    
    mocks["grupos"].obtener_grupo_por_id = AsyncMock(return_value=mock_grupo)
    mocks["usuario_grupo"].obtener_miembros_por_grupo = AsyncMock(
        return_value=[mock_usuario1, mock_usuario2]
    )

    resultado = await servicio.obtener_usuarios_por_grupo(1)

    assert len(resultado) == 2
    assert isinstance(resultado[0], UsuarioSalida)
    mocks["usuario_grupo"].obtener_miembros_por_grupo.assert_awaited_once_with(1)

@pytest.mark.asyncio
async def test_obtener_grupo_por_usuario_retorno_no_existe(servicio, mocks):
    """El usuario no pertenece a un grupo en ese retorno."""
    mocks["usuario_grupo"].obtener_grupo_por_usuario_retorno = AsyncMock(return_value=None)

    with pytest.raises(UsuarioNoEstaEnUnGrupo):
        await servicio.obtener_grupo_por_usuario_retorno(1, 1)

@pytest.mark.asyncio
async def test_obtener_grupo_por_usuario_retorno_exito(servicio, mocks):
    """Caso de éxito: Se obtiene el grupo del usuario."""
    mock_grupo = MagicMock(gr_codigo=1)
    mocks["usuario_grupo"].obtener_grupo_por_usuario_retorno = AsyncMock(return_value=mock_grupo)

    resultado = await servicio.obtener_grupo_por_usuario_retorno(1, 1)

    assert isinstance(resultado, GrupoRetornoRespuesta)
    mocks["usuario_grupo"].obtener_grupo_por_usuario_retorno.assert_awaited_once_with(1, 1)

@pytest.mark.asyncio
async def test_obtener_solicitudes_por_grupo_retorno_vacio(servicio, mocks):
    """El grupo no tiene solicitudes pendientes."""
    mocks["solicitudes"].obtener_solicitudes_por_grupo_retorno = AsyncMock(return_value=[])

    resultado = await servicio.obtener_solicitudes_por_grupo_retorno(1)

    assert resultado == []

@pytest.mark.asyncio
async def test_obtener_solicitudes_por_grupo_retorno_con_solicitudes(servicio, mocks):
    """El grupo tiene solicitudes pendientes."""
    from app.retornos.esquemas.solicitud_grupo_retorno_esquema import SolicitudGrupoRetornoEstado
    from datetime import datetime
    
    mock_solicitud = MagicMock(
        solgr_codigo=1,
        us_codigo=10,
        gr_codigo=1,
        usuario=MagicMock(us_correo="usuario@example.com"),
        solgr_estado=SolicitudGrupoRetornoEstado.PENDIENTE,
        solgr_time_stamp=datetime.now()
    )
    
    mocks["solicitudes"].obtener_solicitudes_por_grupo_retorno = AsyncMock(
        return_value=[mock_solicitud]
    )

    resultado = await servicio.obtener_solicitudes_por_grupo_retorno(1)

    assert len(resultado) == 1
    assert resultado[0].id == 1
    assert resultado[0].correo_usuario == "usuario@example.com"

@pytest.mark.asyncio
async def test_obtener_solicitudes_recientes_por_usuario_vacio(servicio, mocks):
    """El usuario no tiene solicitudes recientes."""
    mocks["solicitudes"].obtener_solicitudes_recientes_por_usuario = AsyncMock(return_value=[])

    resultado = await servicio.obtener_solicitudes_recientes_por_usuario(1)

    assert resultado == []

@pytest.mark.asyncio
async def test_obtener_solicitudes_recientes_por_usuario_con_solicitudes(servicio, mocks):
    """El usuario tiene solicitudes recientes."""
    from app.retornos.esquemas.solicitud_grupo_retorno_esquema import SolicitudGrupoRetornoEstado
    from datetime import datetime
    
    mock_lider = MagicMock(us_nombre="Juan", us_apellido="Pérez")
    mock_solicitud = MagicMock(
        solgr_codigo=1,
        us_codigo=10,
        gr_codigo=1,
        grupo=MagicMock(lider=mock_lider),
        solgr_estado=SolicitudGrupoRetornoEstado.PENDIENTE,
        solgr_time_stamp=datetime.now()
    )
    
    mocks["solicitudes"].obtener_solicitudes_recientes_por_usuario = AsyncMock(
        return_value=[mock_solicitud]
    )

    resultado = await servicio.obtener_solicitudes_recientes_por_usuario(1)

    assert len(resultado) == 1
    assert resultado[0].nombre_lider == "Juan Pérez"

@pytest.mark.asyncio
async def test_rechazar_solicitudes_pendientes_por_usuario(servicio, mocks):
    """Se rechazan todas las solicitudes pendientes del usuario."""
    mocks["solicitudes"].rechazar_solicitudes_pendientes_por_usuario = AsyncMock()

    await servicio._rechazar_solicitudes_pendientes_por_usuario(1)

    mocks["solicitudes"].rechazar_solicitudes_pendientes_por_usuario.assert_awaited_once_with(1)
