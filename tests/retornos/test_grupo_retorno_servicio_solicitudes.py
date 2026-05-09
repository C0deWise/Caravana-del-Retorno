import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi import HTTPException, status
from app.retornos.servicios.grupo_retorno_servicio import GrupoRetornoServicio

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
        mocks["retorno"],
        mocks["grupos"],
        mocks["solicitudes"],
        mocks["usuario_grupo"],
        mocks["usuario"],
        mocks["registro_individual"],
        mocks["registro_grupo"]
    )

@pytest.mark.asyncio
async def test_crear_grupo_retorno_lider_ya_registrado_individual(servicio, mocks):
    """No permite crear grupo si el líder ya tiene registro individual en el retorno actual."""
    mocks["usuario"].obtener_usuario_por_id = AsyncMock(return_value=MagicMock())
    mocks["retorno"].obtener_ultimo_retorno = AsyncMock(return_value=MagicMock(codigo=10))
    mocks["registro_individual"].obtener_registro_retorno_por_usuario_y_retorno = AsyncMock(return_value=MagicMock())

    with pytest.raises(HTTPException) as exc:
        await servicio.crear_grupo_retorno(MagicMock(lider=1))

    assert exc.value.status_code == status.HTTP_400_BAD_REQUEST
    assert "registro de retorno individual" in exc.value.detail

@pytest.mark.asyncio
async def test_crear_grupo_retorno_lider_ya_registrado_grupal(servicio, mocks):
    """No permite crear grupo si el líder ya está inscrito de forma grupal en el retorno actual."""
    mocks["usuario"].obtener_usuario_por_id = AsyncMock(return_value=MagicMock())
    mocks["retorno"].obtener_ultimo_retorno = AsyncMock(return_value=MagicMock(codigo=10))
    mocks["registro_individual"].obtener_registro_retorno_por_usuario_y_retorno = AsyncMock(return_value=None)
    mocks["registro_grupo"].existe_lider_con_grupo_registrado_en_retorno = AsyncMock(return_value=True)

    with pytest.raises(HTTPException) as exc:
        await servicio.crear_grupo_retorno(MagicMock(lider=1))

    assert exc.value.status_code == status.HTTP_400_BAD_REQUEST
    assert "inscrito de forma grupal" in exc.value.detail

@pytest.mark.asyncio
async def test_crear_solicitud_usuario_no_existe(servicio, mocks):
    """Regla 1: El individuo debe existir en el sistema."""
    mocks["usuario"].obtener_usuario_por_id = AsyncMock(return_value=None)

    with pytest.raises(HTTPException) as exc:
        await servicio.crear_solicitud_grupo_retorno(us_codigo=99, gr_codigo=1)
    
    assert exc.value.status_code == status.HTTP_404_NOT_FOUND
    assert "no existe en el sistema" in exc.value.detail

@pytest.mark.asyncio
async def test_crear_solicitud_grupo_no_existe(servicio, mocks):
    """Regla 2: El grupo de retorno debe existir."""
    # El usuario sí existe
    mocks["usuario"].obtener_usuario_por_id = AsyncMock(return_value=MagicMock())
    # Pero el grupo no (devuelve None)
    mocks["grupos"].obtener_grupo_por_id = AsyncMock(return_value=None)

    with pytest.raises(HTTPException) as exc:
        await servicio.crear_solicitud_grupo_retorno(us_codigo=1, gr_codigo=88)
    
    assert exc.value.status_code == status.HTTP_404_NOT_FOUND
    assert "grupo de retorno con ID 88 no existe" in exc.value.detail

@pytest.mark.asyncio
async def test_crear_solicitud_lider_a_si_mismo(servicio, mocks):
    """Nueva Regla: El líder no puede enviarse una solicitud a sí mismo."""
    # El usuario con ID 1 solicita unirse
    mocks["usuario"].obtener_usuario_por_id = AsyncMock(return_value=MagicMock())
    
    # El grupo existe, pero su líder tiene el mismo ID (1)
    mock_grupo = MagicMock(us_codigo_lider=1)
    mocks["grupos"].obtener_grupo_por_id = AsyncMock(return_value=mock_grupo)

    with pytest.raises(HTTPException) as exc:
        await servicio.crear_solicitud_grupo_retorno(us_codigo=1, gr_codigo=10)
    
    assert exc.value.status_code == status.HTTP_400_BAD_REQUEST
    assert "líder del grupo no puede enviarse una solicitud" in exc.value.detail

@pytest.mark.asyncio
async def test_crear_solicitud_usuario_ya_en_grupo_actual(servicio, mocks):
    """Regla 3: El individuo no debe estar ya en un grupo para el último retorno."""
    # Usuario y grupo existen
    mocks["usuario"].obtener_usuario_por_id = AsyncMock(return_value=MagicMock())
    mocks["grupos"].obtener_grupo_por_id = AsyncMock(return_value=MagicMock(us_codigo_lider=999))
    
    # Definimos el retorno actual
    mock_retorno = MagicMock(codigo=10)
    mocks["retorno"].obtener_ultimo_retorno = AsyncMock(return_value=mock_retorno)
    
    # Simular que YA está en un grupo (usuario_grupo_retorno)
    mocks["usuario_grupo"].existe_usuario_en_grupo_para_retorno = AsyncMock(return_value=True)

    with pytest.raises(HTTPException) as exc:
        await servicio.crear_solicitud_grupo_retorno(us_codigo=1, gr_codigo=1)
    
    assert exc.value.status_code == status.HTTP_400_BAD_REQUEST
    assert "ya pertenece a un grupo" in exc.value.detail

@pytest.mark.asyncio
async def test_crear_solicitud_usuario_ya_registrado_individualmente(servicio, mocks):
    """Regla 4: El individuo no puede tener un registro individual (registro_retorno_usuario)."""
    # Usuario y grupo existen
    mocks["usuario"].obtener_usuario_por_id = AsyncMock(return_value=MagicMock())
    mocks["grupos"].obtener_grupo_por_id = AsyncMock(return_value=MagicMock(us_codigo_lider=999))
    
    # Definimos el retorno actual
    mock_retorno = MagicMock(codigo=10)
    mocks["retorno"].obtener_ultimo_retorno = AsyncMock(return_value=mock_retorno)
    
    # No está en grupo...
    mocks["usuario_grupo"].existe_usuario_en_grupo_para_retorno = AsyncMock(return_value=False)
    # ... pero SÍ tiene registro individual
    mocks["registro_individual"].obtener_registro_retorno_por_usuario_y_retorno = AsyncMock(return_value=MagicMock())

    with pytest.raises(HTTPException) as exc:
        await servicio.crear_solicitud_grupo_retorno(us_codigo=1, gr_codigo=1)
    
    assert exc.value.status_code == status.HTTP_400_BAD_REQUEST
    assert "cuenta con un registro de retorno individual" in exc.value.detail

@pytest.mark.asyncio
async def test_crear_solicitud_exito(servicio, mocks):
    """Caso de éxito: Pasa todas las reglas de negocio."""
    # Usuario y grupo existen
    mocks["usuario"].obtener_usuario_por_id = AsyncMock(return_value=MagicMock())
    mocks["grupos"].obtener_grupo_por_id = AsyncMock(return_value=MagicMock(us_codigo_lider=999))
    
    # Definimos el retorno actual
    mock_retorno = MagicMock(codigo=10)
    mocks["retorno"].obtener_ultimo_retorno = AsyncMock(return_value=mock_retorno)
    
    # No está en grupo y no tiene registro individual
    mocks["usuario_grupo"].existe_usuario_en_grupo_para_retorno = AsyncMock(return_value=False)
    mocks["registro_individual"].obtener_registro_retorno_por_usuario_y_retorno = AsyncMock(return_value=None)
    
    # Simular creación exitosa
    mock_solicitud = MagicMock(solgr_codigo=500)
    mocks["solicitudes"].crear_solicitud_grupo_retorno = AsyncMock(return_value=mock_solicitud)

    resultado = await servicio.crear_solicitud_grupo_retorno(us_codigo=1, gr_codigo=1)
    
    assert resultado.solgr_codigo == 500
    mocks["solicitudes"].crear_solicitud_grupo_retorno.assert_called_once_with(1, 1)