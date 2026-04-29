import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import HTTPException, status
from app.retornos.servicios.registro_retorno_grupo_servicio import RegistroRetornoGrupoServicio
from app.retornos.esquemas.registro_retorno_grupo_esquema import RegistroRetornoGrupoCrear, RegistroRetornoGrupoRespuesta
from app.usuarios.schemas.usuario_esquemas import UsuarioSalida

@pytest.fixture
def mocks():
    """Fixture para centralizar la creación de mocks de los repositorios requeridos."""
    return {
        "repo_reg": MagicMock(),
        "repo_grupo": MagicMock(),
        "repo_retorno": MagicMock(),
        "repo_usuario_grupo": MagicMock(),
        "repo_persona": MagicMock()
    }

@pytest.fixture
def servicio(mocks):
    """Instancia el servicio inyectando los mocks."""
    return RegistroRetornoGrupoServicio(
        mocks["repo_reg"],
        mocks["repo_grupo"],
        mocks["repo_retorno"],
        mocks["repo_usuario_grupo"],
        mocks["repo_persona"]
    )

@pytest.fixture
def datos_crear():
    """Esquema de entrada válido para las pruebas de registro."""
    return RegistroRetornoGrupoCrear(
        retorno=1,
        cod_grupo=10,
        num_hospedaje=2,
        num_transporte=1,
        num_parqueadero=0,
        anotacion="Prueba de registro de grupo"
    )

@pytest.mark.asyncio
async def test_crear_registro_grupo_exito(servicio, mocks, datos_crear):
    """Caso de éxito: El grupo cumple todas las condiciones y se registra."""
    # Setup: El grupo existe, el retorno coincide, tiene miembros y no está duplicado
    mocks["repo_grupo"].obtener_grupo_por_id = AsyncMock(return_value=MagicMock())
    mocks["repo_retorno"].obtener_ultimo_retorno = AsyncMock(return_value=MagicMock(codigo=1))
    mocks["repo_usuario_grupo"].contar_miembros_adicionales = AsyncMock(return_value=1)
    mocks["repo_persona"].obtener_personas_por_grupo = AsyncMock(return_value=[]) # No personas para este test
    mocks["repo_reg"].obtener_registro_por_grupo_y_retorno = AsyncMock(return_value=None) 
    
    mock_entidad = MagicMock()
    mocks["repo_reg"].crear_registro_grupo_retorno = AsyncMock(return_value=mock_entidad)

    # Mockeamos la validación del esquema para evitar dependencias de mapeo de nombres en el test
    with patch.object(RegistroRetornoGrupoRespuesta, 'model_validate') as mock_validate:
        mock_validate.return_value = MagicMock(regg_codigo=100)
        
        resultado = await servicio.crear_registro_retorno_grupo(datos_crear)
        
        assert resultado.regg_codigo == 100
        mocks["repo_reg"].crear_registro_grupo_retorno.assert_called_once_with(datos_crear)

@pytest.mark.asyncio
async def test_crear_registro_grupo_no_existe(servicio, mocks, datos_crear):
    """Error: Intento de registrar un grupo que no existe (404)."""
    mocks["repo_grupo"].obtener_grupo_por_id = AsyncMock(return_value=None)

    with pytest.raises(HTTPException) as exc:
        await servicio.crear_registro_retorno_grupo(datos_crear)
    
    assert exc.value.status_code == status.HTTP_404_NOT_FOUND
    assert "no existe" in exc.value.detail

@pytest.mark.asyncio
async def test_crear_registro_retorno_no_vigente(servicio, mocks, datos_crear):
    """Error: Se intenta registrar en un retorno que no es el último vigente (400)."""
    mocks["repo_grupo"].obtener_grupo_por_id = AsyncMock(return_value=MagicMock())
    # El último en el sistema es el 2, pero los datos piden el 1
    mocks["repo_retorno"].obtener_ultimo_retorno = AsyncMock(return_value=MagicMock(codigo=2))

    with pytest.raises(HTTPException) as exc:
        await servicio.crear_registro_retorno_grupo(datos_crear)
    
    assert exc.value.status_code == status.HTTP_400_BAD_REQUEST
    assert "último retorno vigente" in exc.value.detail

@pytest.mark.asyncio
async def test_crear_registro_sin_integrantes_suficientes(servicio, mocks, datos_crear):
    """Error: El grupo no tiene miembros adicionales al líder (400)."""
    mocks["repo_grupo"].obtener_grupo_por_id = AsyncMock(return_value=MagicMock())
    mocks["repo_retorno"].obtener_ultimo_retorno = AsyncMock(return_value=MagicMock(codigo=1))
    mocks["repo_usuario_grupo"].contar_miembros_adicionales = AsyncMock(return_value=0) # No usuarios adicionales
    mocks["repo_persona"].obtener_personas_por_grupo = AsyncMock(return_value=[]) # No personas

    with pytest.raises(HTTPException) as exc:
        await servicio.crear_registro_retorno_grupo(datos_crear)
    
    assert exc.value.status_code == status.HTTP_400_BAD_REQUEST
    assert "al menos un integrante (usuario o persona)" in exc.value.detail # Mensaje de error actualizado

@pytest.mark.asyncio
async def test_crear_registro_duplicado(servicio, mocks, datos_crear):
    """Error: El grupo ya fue registrado previamente para este retorno (409)."""
    mocks["repo_grupo"].obtener_grupo_por_id = AsyncMock(return_value=MagicMock())
    mocks["repo_retorno"].obtener_ultimo_retorno = AsyncMock(return_value=MagicMock(codigo=1))
    mocks["repo_usuario_grupo"].contar_miembros_adicionales = AsyncMock(return_value=2)
    # El repo devuelve que ya existe un registro
    mocks["repo_persona"].obtener_personas_por_grupo = AsyncMock(return_value=[]) # No personas para este test
    mocks["repo_reg"].obtener_registro_por_grupo_y_retorno = AsyncMock(return_value=MagicMock())

    with pytest.raises(HTTPException) as exc:
        await servicio.crear_registro_retorno_grupo(datos_crear)
    
    assert exc.value.status_code == status.HTTP_409_CONFLICT

@pytest.mark.asyncio
async def test_obtener_usuarios_por_grupo_exito(servicio, mocks):
    """Caso de éxito: Se recuperan los miembros de un grupo existente."""
    mocks["repo_grupo"].obtener_grupo_por_id = AsyncMock(return_value=MagicMock())
    mocks["repo_usuario_grupo"].obtener_miembros_por_grupo = AsyncMock(return_value=[MagicMock(), MagicMock()])

    with patch.object(UsuarioSalida, 'model_validate', return_value=MagicMock()):
        resultado = await servicio.obtener_usuarios_por_grupo(10)
        assert len(resultado) == 2
        mocks["repo_usuario_grupo"].obtener_miembros_por_grupo.assert_called_once_with(10)

@pytest.mark.asyncio
async def test_crear_registro_grupo_solo_personas(servicio, mocks, datos_crear):
    """Caso de éxito: El grupo tiene personas pero no usuarios adicionales al líder."""
    # Setup: El grupo existe, el retorno coincide, tiene miembros y no está duplicado
    mocks["repo_grupo"].obtener_grupo_por_id = AsyncMock(return_value=MagicMock())
    mocks["repo_retorno"].obtener_ultimo_retorno = AsyncMock(return_value=MagicMock(codigo=1))
    mocks["repo_usuario_grupo"].contar_miembros_adicionales = AsyncMock(return_value=0) # No usuarios adicionales
    mocks["repo_persona"].obtener_personas_por_grupo = AsyncMock(return_value=[MagicMock()]) # Una persona
    mocks["repo_reg"].obtener_registro_por_grupo_y_retorno = AsyncMock(return_value=None)
    
    mock_entidad = MagicMock()
    mocks["repo_reg"].crear_registro_grupo_retorno = AsyncMock(return_value=mock_entidad)

    # Mockeamos la validación del esquema para evitar dependencias de mapeo de nombres en el test
    with patch.object(RegistroRetornoGrupoRespuesta, 'model_validate') as mock_validate:
        mock_validate.return_value = MagicMock(regg_codigo=100)
        
        resultado = await servicio.crear_registro_retorno_grupo(datos_crear)
        
        assert resultado.regg_codigo == 100
        mocks["repo_reg"].crear_registro_grupo_retorno.assert_called_once_with(datos_crear)

@pytest.mark.asyncio
async def test_crear_registro_grupo_usuarios_y_personas(servicio, mocks, datos_crear):
    """Caso de éxito: El grupo tiene usuarios adicionales y personas."""
    mocks["repo_grupo"].obtener_grupo_por_id = AsyncMock(return_value=MagicMock())
    mocks["repo_retorno"].obtener_ultimo_retorno = AsyncMock(return_value=MagicMock(codigo=1))
    mocks["repo_usuario_grupo"].contar_miembros_adicionales = AsyncMock(return_value=1) # Un usuario adicional
    mocks["repo_persona"].obtener_personas_por_grupo = AsyncMock(return_value=[MagicMock(), MagicMock()]) # Dos personas
    mocks["repo_reg"].obtener_registro_por_grupo_y_retorno = AsyncMock(return_value=None)
    
    mock_entidad = MagicMock()
    mocks["repo_reg"].crear_registro_grupo_retorno = AsyncMock(return_value=mock_entidad)

    with patch.object(RegistroRetornoGrupoRespuesta, 'model_validate') as mock_validate:
        mock_validate.return_value = MagicMock(regg_codigo=100)
        
        resultado = await servicio.crear_registro_retorno_grupo(datos_crear)
        
        assert resultado.regg_codigo == 100
        mocks["repo_reg"].crear_registro_grupo_retorno.assert_called_once_with(datos_crear)