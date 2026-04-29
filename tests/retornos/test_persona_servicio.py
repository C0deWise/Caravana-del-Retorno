import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi import HTTPException, status
from app.retornos.modelos.persona_modelo import TipoDoc
from app.retornos.servicios.persona_servicio import PersonaServicio
from app.retornos.esquemas.persona_esquema import PersonaCrear

@pytest.fixture
def mocks():
    """Fixture para centralizar los mocks de los repositorios."""
    return {
        "repositorio": MagicMock(),
        "repo_retorno": MagicMock(),
        "repo_reg_grupo": MagicMock()
    }

@pytest.fixture
def servicio(mocks):
    """Instancia el servicio inyectando los mocks."""
    return PersonaServicio(
        mocks["repositorio"],
        mocks["repo_retorno"],
        mocks["repo_reg_grupo"]
    )

@pytest.fixture
def datos_persona():
    """Datos base para crear una persona."""
    return PersonaCrear(
        pe_tipo_doc=  TipoDoc.CC,
        pe_documento="12345678",
        pe_nombre="Juan",
        pe_apellido="Pérez",
        pe_correo="juan.perez@example.com",
        pe_fecha_nacimiento="1990-01-01"
    )

@pytest.mark.asyncio
async def test_crear_persona_documento_duplicado(servicio, mocks, datos_persona):
    """Restricción: No debe haber dos personas con el mismo documento."""
    # Simulamos que ya existe una persona con ese documento
    mocks["repositorio"].obtener_por_documento = AsyncMock(return_value=MagicMock())

    with pytest.raises(HTTPException) as exc:
        await servicio.crear_persona(datos_persona)
    
    assert exc.value.status_code == 400
    assert "documento" in exc.value.detail.lower()

@pytest.mark.asyncio
async def test_crear_persona_correo_duplicado(servicio, mocks, datos_persona):
    """Restricción: No debe haber dos personas con el mismo correo."""
    # No hay duplicado de documento
    mocks["repositorio"].obtener_por_documento = AsyncMock(return_value=None)
    # Pero sí hay duplicado de correo
    mocks["repositorio"].obtener_por_correo = AsyncMock(return_value=MagicMock())

    with pytest.raises(HTTPException) as exc:
        await servicio.crear_persona(datos_persona)
    
    assert exc.value.status_code == 400
    assert "correo" in exc.value.detail.lower()

@pytest.mark.asyncio
async def test_asociar_persona_no_existe(servicio, mocks):
    """Restricción: La persona debe existir."""
    mocks["repositorio"].obtener_por_id = AsyncMock(return_value=None)

    with pytest.raises(HTTPException) as exc:
        await servicio.asociar_persona_a_grupo(pe_codigo=999, gr_codigo=1)
    
    assert exc.value.status_code == 404
    assert "no encontrada" in exc.value.detail.lower()

@pytest.mark.asyncio
async def test_asociar_grupo_no_registrado_o_no_existe(servicio, mocks):
    """Restricción: El grupo debe existir y estar registrado en el retorno actual."""
    # Persona existe
    mocks["repositorio"].obtener_por_id = AsyncMock(return_value=MagicMock())
    # Hay un retorno vigente
    mock_retorno = MagicMock()
    mock_retorno.codigo = 5
    mocks["repo_retorno"].obtener_ultimo_retorno = AsyncMock(return_value=mock_retorno)
    
    # El grupo NO está registrado para ese retorno (o no existe)
    mocks["repo_reg_grupo"].obtener_registro_por_grupo_y_retorno = AsyncMock(return_value=None)

    with pytest.raises(HTTPException) as exc:
        await servicio.asociar_persona_a_grupo(pe_codigo=1, gr_codigo=10)
    
    assert exc.value.status_code == 400
    assert "no está registrado" in exc.value.detail.lower()

@pytest.mark.asyncio
async def test_asociar_persona_ya_en_otro_grupo_del_retorno(servicio, mocks):
    """Restricción: Una persona solo puede pertenecer a un Grupo_retorno por retorno."""
    # Persona existe
    mocks["repositorio"].obtener_por_id = AsyncMock(return_value=MagicMock())
    # Hay un retorno vigente
    mock_retorno = MagicMock()
    mock_retorno.codigo = 5
    mocks["repo_retorno"].obtener_ultimo_retorno = AsyncMock(return_value=mock_retorno)
    
    # El grupo sí está registrado
    mocks["repo_reg_grupo"].obtener_registro_por_grupo_y_retorno = AsyncMock(return_value=MagicMock())
    
    # RESTRICCIÓN CLAVE: La persona ya está inscrita en este retorno
    mocks["repositorio"].persona_ya_en_retorno = AsyncMock(return_value=True)

    with pytest.raises(HTTPException) as exc:
        await servicio.asociar_persona_a_grupo(pe_codigo=1, gr_codigo=10)
    
    assert exc.value.status_code == 400
    assert "ya pertenece a un grupo" in exc.value.detail.lower()