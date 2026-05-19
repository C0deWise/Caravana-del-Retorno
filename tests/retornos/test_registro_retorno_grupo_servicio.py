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
        num_parqueadero_carro=0,
        num_parqueadero_moto=1,
        anotacion="Prueba de registro de grupo"
    )

# ===== HELPERS =====

def setup_crear_registro_mocks(mocks, grupo_lider=1, retorno_codigo=1, retorno_estado="activo",
                                usuarios_adicionales=2, personas=None, ya_registrado=False):
    """Helper para configurar mocks comunes en pruebas de crear_registro_retorno_grupo."""
    personas = personas or []
    
    mock_grupo = MagicMock(us_codigo_lider=grupo_lider)
    mocks["repo_grupo"].obtener_grupo_por_id = AsyncMock(return_value=mock_grupo)
    mocks["repo_retorno"].obtener_ultimo_retorno = AsyncMock(
        return_value=MagicMock(codigo=retorno_codigo, estado=retorno_estado)
    )
    mocks["repo_usuario_grupo"].contar_miembros_adicionales = AsyncMock(return_value=usuarios_adicionales)
    mocks["repo_persona"].obtener_personas_por_grupo = AsyncMock(return_value=personas)
    mocks["repo_reg"].obtener_registro_por_grupo_y_retorno = AsyncMock(
        return_value=MagicMock() if ya_registrado else None
    )
    mocks["repo_usuario_grupo"].asociar_usuario_a_grupo_retorno = AsyncMock()
    
    mock_entidad = MagicMock()
    mocks["repo_reg"].crear_registro_grupo_retorno = AsyncMock(return_value=mock_entidad)

def setup_consultar_registro_mocks(mocks, retorno_existe=True, grupo_existe=True, registro_existe=True):
    """Helper para configurar mocks comunes en pruebas de consultar_registro_por_grupo_y_retorno."""
    mocks["repo_retorno"].get_by_codigo = AsyncMock(
        return_value=MagicMock() if retorno_existe else None
    )
    mocks["repo_grupo"].obtener_grupo_por_id = AsyncMock(
        return_value=MagicMock() if grupo_existe else None
    )
    mocks["repo_reg"].obtener_registro_por_grupo_y_retorno = AsyncMock(
        return_value=MagicMock() if registro_existe else None
    )

def create_estado_mock(valor="activo"):
    """Helper para crear un mock de Enum estado."""
    estado = MagicMock()
    estado.value = valor
    estado.__eq__ = lambda self, other: other == valor
    estado.__ne__ = lambda self, other: other != valor
    return estado

# ===== PRUEBAS: crear_registro_retorno_grupo =====

@pytest.mark.asyncio
async def test_crear_registro_grupo_exito(servicio, mocks, datos_crear):
    """Caso de éxito: El grupo cumple todas las condiciones y se registra."""
    setup_crear_registro_mocks(mocks)

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
    mocks["repo_retorno"].obtener_ultimo_retorno = AsyncMock(return_value=MagicMock(codigo=2))

    with pytest.raises(HTTPException) as exc:
        await servicio.crear_registro_retorno_grupo(datos_crear)
    
    assert exc.value.status_code == status.HTTP_400_BAD_REQUEST
    assert "último retorno vigente" in exc.value.detail

@pytest.mark.asyncio
async def test_crear_registro_sin_integrantes_suficientes(servicio, mocks, datos_crear):
    """Error: El grupo no tiene suficientes integrantes para los servicios solicitados (400)."""
    setup_crear_registro_mocks(mocks, usuarios_adicionales=0, personas=[])

    with pytest.raises(HTTPException) as exc:
        await servicio.crear_registro_retorno_grupo(datos_crear)
    
    assert exc.value.status_code == status.HTTP_400_BAD_REQUEST
    assert "hospedajes" in exc.value.detail

@pytest.mark.asyncio
async def test_crear_registro_duplicado(servicio, mocks, datos_crear):
    """Error: El grupo ya fue registrado previamente para este retorno (409)."""
    setup_crear_registro_mocks(mocks, ya_registrado=True)

    with pytest.raises(HTTPException) as exc:
        await servicio.crear_registro_retorno_grupo(datos_crear)
    
    assert exc.value.status_code == status.HTTP_409_CONFLICT

@pytest.mark.asyncio
async def test_crear_registro_grupo_solo_personas(servicio, mocks, datos_crear):
    """Caso de éxito: El grupo tiene personas pero no usuarios adicionales al líder."""
    setup_crear_registro_mocks(mocks, usuarios_adicionales=0, personas=[MagicMock(), MagicMock()])

    with patch.object(RegistroRetornoGrupoRespuesta, 'model_validate') as mock_validate:
        mock_validate.return_value = MagicMock(regg_codigo=100)
        
        resultado = await servicio.crear_registro_retorno_grupo(datos_crear)
        
        assert resultado.regg_codigo == 100

@pytest.mark.asyncio
async def test_crear_registro_grupo_usuarios_y_personas(servicio, mocks, datos_crear):
    """Caso de éxito: El grupo tiene usuarios adicionales y personas."""
    setup_crear_registro_mocks(mocks, usuarios_adicionales=1, personas=[MagicMock(), MagicMock()])

    with patch.object(RegistroRetornoGrupoRespuesta, 'model_validate') as mock_validate:
        mock_validate.return_value = MagicMock(regg_codigo=100)
        
        resultado = await servicio.crear_registro_retorno_grupo(datos_crear)
        
        assert resultado.regg_codigo == 100

# ===== PRUEBAS: obtener_miembros_por_grupo =====

@pytest.mark.asyncio
async def test_obtener_miembros_por_grupo_exito(servicio, mocks):
    """Caso de éxito: Se recuperan todos los miembros de un grupo (usuarios + personas)."""
    mocks["repo_grupo"].obtener_grupo_por_id = AsyncMock(return_value=MagicMock())
    mock_miembro1 = MagicMock()
    mock_miembro2 = MagicMock()
    mocks["repo_usuario_grupo"].obtener_miembros_por_grupo = AsyncMock(return_value=[mock_miembro1, mock_miembro2])
    mock_persona = MagicMock(pe_codigo=1, pe_nombre="Juan", pe_apellido="Pérez", pe_correo="juan@test.com", pe_documento="123456")
    mocks["repo_persona"].obtener_personas_por_grupo = AsyncMock(return_value=[mock_persona])

    with patch.object(UsuarioSalida, 'model_validate', return_value=MagicMock()):
        resultado = await servicio.obtener_miembros_por_grupo(10)
        assert len(resultado) == 3

# ===== PRUEBAS: consultar_registro_por_grupo_y_retorno =====

@pytest.mark.asyncio
async def test_consultar_registro_exito(servicio, mocks):
    """Caso de éxito: Se consulta un registro existente de un grupo en un retorno."""
    setup_consultar_registro_mocks(mocks)

    with patch.object(RegistroRetornoGrupoRespuesta, 'model_validate') as mock_validate:
        mock_validate.return_value = MagicMock(regg_codigo=100)
        
        resultado = await servicio.consultar_registro_por_grupo_y_retorno(10, 1)
        
        assert resultado.regg_codigo == 100
        mocks["repo_retorno"].get_by_codigo.assert_called_once_with(1)
        mocks["repo_grupo"].obtener_grupo_por_id.assert_called_once_with(10)

@pytest.mark.asyncio
async def test_consultar_registro_retorno_no_existe(servicio, mocks):
    """Error: Se intenta consultar un registro para un retorno que no existe (404)."""
    setup_consultar_registro_mocks(mocks, retorno_existe=False)

    with pytest.raises(HTTPException) as exc:
        await servicio.consultar_registro_por_grupo_y_retorno(10, 999)
    
    assert exc.value.status_code == status.HTTP_404_NOT_FOUND

@pytest.mark.asyncio
async def test_consultar_registro_grupo_no_existe(servicio, mocks):
    """Error: Se intenta consultar un registro para un grupo que no existe (404)."""
    setup_consultar_registro_mocks(mocks, grupo_existe=False)

    with pytest.raises(HTTPException) as exc:
        await servicio.consultar_registro_por_grupo_y_retorno(999, 1)
    
    assert exc.value.status_code == status.HTTP_404_NOT_FOUND

@pytest.mark.asyncio
async def test_consultar_registro_no_existe_para_grupo_y_retorno(servicio, mocks):
    """Error: No existe un registro para la combinación de grupo y retorno especificada (404)."""
    setup_consultar_registro_mocks(mocks, registro_existe=False)

    with pytest.raises(HTTPException) as exc:
        await servicio.consultar_registro_por_grupo_y_retorno(10, 1)
    
    assert exc.value.status_code == status.HTTP_404_NOT_FOUND

# PRUEBAS: EDITAR REGISTRO RETORNO GRUPO

@pytest.mark.asyncio
async def test_editar_registro_retorno_grupo_exitoso(servicio, mocks):
    datos_editar = MagicMock()
    datos_editar.num_hospedaje = 3
    datos_editar.num_transporte = 2

    mock_registro = MagicMock(retorno=1)
    mocks["repo_reg"].obtener_registro_por_id =AsyncMock(return_value=mock_registro)

    mock_retorno = MagicMock(estado="activo")
    mocks["repo_retorno"].get_by_codigo = AsyncMock(return_value=mock_retorno)

    mock_registro_actualizado = MagicMock()
    mocks["repo_reg"].editar_registro_grupo_retorno = AsyncMock(return_value=mock_registro_actualizado)

    with patch.object(RegistroRetornoGrupoRespuesta, 'model_validate') as mock_validate:
        mock_validate.return_value = MagicMock(regg_codigo=1)

        resultado = await servicio.editar_registro_retorno_grupo(1, datos_editar)

        assert resultado.regg_codigo == 1
        mocks["repo_reg"].obtener_registro_por_id.assert_called_once_with(1)
        mocks["repo_retorno"].get_by_codigo.assert_called_once_with(1)
        mocks["repo_reg"].editar_registro_grupo_retorno.assert_called_once_with(1, datos_editar)

@pytest.mark.asyncio
async def test_editar_registro_grupo_no_existente(servicio, mocks):
    datos_editar = MagicMock()
    mocks["repo_reg"].obtener_registro_por_id = AsyncMock(return_value=None)

    with pytest.raises(HTTPException) as exc:
        await servicio.editar_registro_retorno_grupo(999, datos_editar)
    
    assert exc.value.status_code == status.HTTP_404_NOT_FOUND
    assert "no existe" in exc.value.detail

@pytest.mark.asyncio
async def test_editar_registro_retorno_no_existe(servicio, mocks):
    datos_editar = MagicMock()
    mock_registro = MagicMock(retorno=999)
    mocks["repo_reg"].obtener_registro_por_id = AsyncMock(return_value=mock_registro)
    mocks["repo_retorno"].get_by_codigo = AsyncMock(return_value=None)

    with pytest.raises(HTTPException) as exc:
        await servicio.editar_registro_retorno_grupo(1, datos_editar)
    
    assert exc.value.status_code == status.HTTP_404_NOT_FOUND
    assert "no existe" in exc.value.detail

async def test_editar_registro_retorno_no_activo(servicio, mocks):
    datos_editar = MagicMock()
    mock_registro = MagicMock(retorno=1)
    mocks["repo_reg"].obtener_registro_por_id = AsyncMock(return_value=mock_registro)
    mock_retorno = create_estado_mock("finalizado")
    mocks["repo_retorno"].get_by_codigo = AsyncMock(return_value=mock_retorno)

    with pytest.raises(HTTPException) as exc:
        await servicio.editar_registro_retorno_grupo(1, datos_editar)
    
    assert exc.value.status_code == status.HTTP_409_CONFLICT
    assert "No es posible editar este registro" in exc.value.detail