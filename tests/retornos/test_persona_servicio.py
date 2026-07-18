from app.retornos.esquemas.retorno_esquemas import RetornoEstado
import pytest
from datetime import date
from unittest.mock import AsyncMock, MagicMock
from fastapi import HTTPException, status
from app.retornos.servicios.persona_servicio import PersonaServicio
from app.retornos.esquemas.persona_esquema import PersonaCrear
from app.retornos.excepciones.persona_excepciones import PersonaNoEncontrada
from app.retornos.excepciones.grupo_excepciones import GrupoNoEncontrado
from app.retornos.modelos.persona_modelo import Genero, TipoDoc


@pytest.fixture
def mocks():
    """Fixture para centralizar los mocks de los repositorios."""
    return {
        "repositorio": MagicMock(),
        "repo_retorno": MagicMock(),
        "repo_grupo": MagicMock()
    }


@pytest.fixture
def servicio(mocks):
    """Instancia el servicio inyectando los mocks."""
    return PersonaServicio(
        mocks["repositorio"],
        mocks["repo_retorno"],
        mocks["repo_grupo"]
    )


@pytest.fixture
def datos_persona():
    """Datos base para crear una persona."""
    return PersonaCrear(
        pe_tipo_doc=TipoDoc.CC,
        pe_documento="12345678",
        pe_nombre="Juan",
        pe_apellido="Pérez",
        pe_correo="juan.perez@example.com",
        pe_fecha_nacimiento=date(1990, 1, 1),
        pe_genero=Genero.M
    )

@pytest.fixture
def persona_mock():
    """Mock de una persona con todos los atributos válidos."""
    mock = MagicMock()
    mock.pe_codigo = 1
    mock.pe_tipo_doc = TipoDoc.CC
    mock.pe_documento = "12345678"
    mock.pe_nombre = "Juan"
    mock.pe_apellido = "Pérez"
    mock.pe_correo = "juan@example.com"
    mock.pe_fecha_nacimiento = date(1990, 1, 1)
    mock.pe_genero = Genero.M
    return mock

@pytest.fixture
def persona_dos_mock():
    """Mock de una segunda persona."""
    mock = MagicMock()
    mock.pe_codigo = 2
    mock.pe_tipo_doc = TipoDoc.CE
    mock.pe_documento = "87654321"
    mock.pe_nombre = "María"
    mock.pe_apellido = "García"
    mock.pe_correo = "maria@example.com"
    mock.pe_fecha_nacimiento = date(1992, 5, 15)
    mock.pe_genero = Genero.F
    return mock

@pytest.fixture
def grupo_mock():
    """Mock de un grupo de retorno."""
    mock = MagicMock()
    mock.gr_codigo = 1
    mock.gr_nombre = "Grupo Test"
    return mock

@pytest.fixture
def asociacion_mock():
    """Mock de una asociación persona-grupo."""
    mock = MagicMock()
    mock.pgr_codigo = 1
    mock.pe_codigo = 1
    mock.gr_codigo = 1
    return mock

@pytest.fixture
def retorno_mock():
    """Mock de un retorno vigente."""
    mock = MagicMock()
    mock.codigo = 5
    mock.estado = RetornoEstado.ACTIVO
    return mock

@pytest.mark.asyncio
async def test_crear_persona_exito(servicio, mocks, datos_persona, persona_mock):
    """Caso de éxito: Se crea una persona correctamente."""
    mocks["repositorio"].obtener_por_documento = AsyncMock(return_value=None)
    mocks["repositorio"].obtener_por_correo = AsyncMock(return_value=None)
    mocks["repositorio"].crear_persona = AsyncMock(return_value=persona_mock)

    resultado = await servicio.crear_persona(datos_persona)

    assert resultado.pe_codigo == 1
    assert resultado.pe_nombre == "Juan"
    mocks["repositorio"].crear_persona.assert_called_once_with(datos_persona)

@pytest.mark.asyncio
async def test_crear_persona_documento_duplicado(servicio, mocks, datos_persona):
    """Restricción: No debe haber dos personas con el mismo documento."""
    mocks["repositorio"].obtener_por_documento = AsyncMock(return_value=MagicMock())

    with pytest.raises(HTTPException) as exc:
        await servicio.crear_persona(datos_persona)

    assert exc.value.status_code == 400
    assert "documento" in exc.value.detail.lower()

@pytest.mark.asyncio
async def test_crear_persona_correo_duplicado(servicio, mocks, datos_persona):
    """Restricción: No debe haber dos personas con el mismo correo."""
    mocks["repositorio"].obtener_por_documento = AsyncMock(return_value=None)
    mocks["repositorio"].obtener_por_correo = AsyncMock(return_value=MagicMock())

    with pytest.raises(HTTPException) as exc:
        await servicio.crear_persona(datos_persona)

    assert exc.value.status_code == 400
    assert "correo" in exc.value.detail.lower()

@pytest.mark.asyncio
async def test_asociar_persona_a_grupo_exito(servicio, mocks, persona_mock, grupo_mock, retorno_mock, asociacion_mock):
    """Caso de éxito: Se asocia una persona a un grupo."""
    mocks["repositorio"].obtener_por_id = AsyncMock(return_value=persona_mock)
    mocks["repo_retorno"].obtener_ultimo_retorno = AsyncMock(return_value=retorno_mock)
    mocks["repo_grupo"].obtener_grupo_por_id = AsyncMock(return_value=grupo_mock)
    mocks["repositorio"].persona_ya_en_retorno = AsyncMock(return_value=False)
    mocks["repositorio"].asociar_a_grupo = AsyncMock(return_value=asociacion_mock)

    resultado = await servicio.asociar_persona_a_grupo(pe_codigo=1, gr_codigo=1)

    assert resultado is not None
    mocks["repositorio"].asociar_a_grupo.assert_called_once_with(1, 1)


@pytest.mark.asyncio
async def test_asociar_persona_no_existe(servicio, mocks):
    """Restricción: La persona debe existir."""
    mocks["repositorio"].obtener_por_id = AsyncMock(return_value=None)

    with pytest.raises(PersonaNoEncontrada):
        await servicio.asociar_persona_a_grupo(pe_codigo=999, gr_codigo=1)

@pytest.mark.asyncio
async def test_asociar_sin_retorno_vigente(servicio, mocks, persona_mock):
    """Restricción: Debe existir un retorno vigente en el sistema."""
    mocks["repositorio"].obtener_por_id = AsyncMock(return_value=persona_mock)
    mocks["repo_retorno"].obtener_ultimo_retorno = AsyncMock(return_value=None)

    with pytest.raises(HTTPException) as exc:
        await servicio.asociar_persona_a_grupo(pe_codigo=1, gr_codigo=1)

    assert exc.value.status_code == 400
    assert "retorno" in exc.value.detail.lower()

@pytest.mark.asyncio
async def test_asociar_grupo_no_existe(servicio, mocks, persona_mock, retorno_mock):
    """Restricción: El grupo debe existir."""
    mocks["repositorio"].obtener_por_id = AsyncMock(return_value=persona_mock)
    mocks["repo_retorno"].obtener_ultimo_retorno = AsyncMock(return_value=retorno_mock)
    mocks["repo_grupo"].obtener_grupo_por_id = AsyncMock(return_value=None)

    with pytest.raises(GrupoNoEncontrado):
        await servicio.asociar_persona_a_grupo(pe_codigo=1, gr_codigo=10)

@pytest.mark.asyncio
async def test_asociar_persona_ya_en_otro_grupo_del_retorno(servicio, mocks, persona_mock, grupo_mock, retorno_mock):
    """Restricción: Una persona solo puede pertenecer a un Grupo_retorno por retorno."""
    mocks["repositorio"].obtener_por_id = AsyncMock(return_value=persona_mock)
    mocks["repo_retorno"].obtener_ultimo_retorno = AsyncMock(return_value=retorno_mock)
    mocks["repo_grupo"].obtener_grupo_por_id = AsyncMock(return_value=grupo_mock)
    mocks["repositorio"].persona_ya_en_retorno = AsyncMock(return_value=True)

    with pytest.raises(HTTPException) as exc:
        await servicio.asociar_persona_a_grupo(pe_codigo=1, gr_codigo=10)

    assert exc.value.status_code == 400
    assert "ya pertenece a un grupo" in exc.value.detail.lower()

@pytest.mark.asyncio
async def test_listar_personas_exito(servicio, mocks, persona_mock, persona_dos_mock):
    """Caso de éxito: Se listan todas las personas."""

    mocks["repositorio"].obtener_todas_las_personas = AsyncMock(return_value=[persona_mock, persona_dos_mock])

    resultado = await servicio.listar_personas()

    assert len(resultado) == 2
    assert resultado[0].pe_codigo == 1
    assert resultado[1].pe_codigo == 2

@pytest.mark.asyncio
async def test_listar_personas_vacio(servicio, mocks):
    """Caso: No hay personas registradas."""
    mocks["repositorio"].obtener_todas_las_personas = AsyncMock(return_value=[])

    resultado = await servicio.listar_personas()

    assert resultado == []

@pytest.mark.asyncio
async def test_listar_personas_por_grupo_exito(servicio, mocks, persona_mock, persona_dos_mock):
    """Caso de éxito: Se listan personas de un grupo."""
    mocks["repositorio"].obtener_personas_por_grupo = AsyncMock(return_value=[persona_mock, persona_dos_mock])

    resultado = await servicio.listar_personas_por_grupo(gr_codigo=1)

    assert len(resultado) == 2
    mocks["repositorio"].obtener_personas_por_grupo.assert_called_once_with(1)

@pytest.mark.asyncio
async def test_listar_personas_por_grupo_vacio(servicio, mocks):
    """Caso: El grupo no tiene personas."""
    mocks["repositorio"].obtener_personas_por_grupo = AsyncMock(return_value=[])

    resultado = await servicio.listar_personas_por_grupo(gr_codigo=1)

    assert resultado == []

@pytest.mark.asyncio
async def test_obtener_persona_por_id_exito(servicio, mocks, persona_mock):
    """Caso de éxito: Se obtiene una persona por ID."""
    mocks["repositorio"].obtener_por_id = AsyncMock(return_value=persona_mock)

    resultado = await servicio.obtener_persona_por_id(pe_codigo=1)

    assert resultado.pe_codigo == 1
    assert resultado.pe_nombre == "Juan"

@pytest.mark.asyncio
async def test_obtener_persona_por_id_no_existe(servicio, mocks):
    """Restricción: La persona debe existir."""
    mocks["repositorio"].obtener_por_id = AsyncMock(return_value=None)

    with pytest.raises(PersonaNoEncontrada):
        await servicio.obtener_persona_por_id(pe_codigo=999)

@pytest.mark.asyncio
async def test_obtener_persona_por_documento_exito(servicio, mocks, persona_mock):
    """Caso de éxito: Se obtiene una persona por documento."""
    mocks["repositorio"].obtener_por_documento = AsyncMock(return_value=persona_mock)

    resultado = await servicio.obtener_persona_por_documento(documento="12345678")

    assert resultado.pe_documento == "12345678"
    assert resultado.pe_nombre == "Juan"

@pytest.mark.asyncio
async def test_obtener_persona_por_documento_no_existe(servicio, mocks):
    """Restricción: La persona debe existir."""
    mocks["repositorio"].obtener_por_documento = AsyncMock(return_value=None)

    with pytest.raises(PersonaNoEncontrada):
        await servicio.obtener_persona_por_documento(documento="99999999")

@pytest.mark.asyncio
async def test_verificar_registro_retorno_persona_verdadero(servicio, mocks):
    """Caso: La persona está registrada en el retorno."""
    mocks["repositorio"].persona_ya_en_retorno = AsyncMock(return_value=MagicMock())

    resultado = await servicio.verificar_registro_retorno_persona(pe_codigo=1, re_codigo=5)

    assert resultado is True

@pytest.mark.asyncio
async def test_verificar_registro_retorno_persona_falso(servicio, mocks):
    """Caso: La persona NO está registrada en el retorno."""
    mocks["repositorio"].persona_ya_en_retorno = AsyncMock(return_value=None)

    resultado = await servicio.verificar_registro_retorno_persona(pe_codigo=1, re_codigo=5)

    assert resultado is False

@pytest.mark.asyncio
async def test_verificar_registro_retorno_persona_por_documento_exito(servicio, mocks, persona_mock):
    """Caso de éxito: Se verifica registro por documento."""
    mocks["repositorio"].obtener_por_documento = AsyncMock(return_value=persona_mock)
    mocks["repositorio"].persona_ya_en_retorno = AsyncMock(return_value=MagicMock())

    resultado = await servicio.verificar_registro_retorno_persona_por_documento(
        pe_documento="12345678",
        re_codigo=5
    )

    assert resultado is True

@pytest.mark.asyncio
async def test_verificar_registro_retorno_persona_por_documento_no_existe(servicio, mocks):
    """Restricción: La persona debe existir."""
    mocks["repositorio"].obtener_por_documento = AsyncMock(return_value=None)

    with pytest.raises(HTTPException) as exc:
        await servicio.verificar_registro_retorno_persona_por_documento(
            pe_documento="99999999",
            re_codigo=5
        )

    assert exc.value.status_code == 404
    assert "no encontrada" in exc.value.detail.lower()

@pytest.mark.asyncio
async def test_remover_persona_grupo_exito(servicio, mocks, persona_mock, grupo_mock):
    """Caso de éxito: Se remueve una persona de un grupo."""
    mocks["repositorio"].obtener_por_id = AsyncMock(return_value=persona_mock)
    mocks["repo_grupo"].obtener_grupo_por_id = AsyncMock(return_value=grupo_mock)
    mocks["repositorio"].persona_esta_en_grupo = AsyncMock(return_value=True)
    mocks["repositorio"].remover_persona_grupo_retorno = AsyncMock(return_value=True)

    resultado = await servicio.remover_persona_grupo_retorno(pe_codigo=1, gr_codigo=1)

    assert resultado is True
    mocks["repositorio"].remover_persona_grupo_retorno.assert_called_once_with(1, 1)

@pytest.mark.asyncio
async def test_remover_persona_no_existe(servicio, mocks):
    """Restricción: La persona debe existir."""
    mocks["repositorio"].obtener_por_id = AsyncMock(return_value=None)

    with pytest.raises(PersonaNoEncontrada):
        await servicio.remover_persona_grupo_retorno(pe_codigo=999, gr_codigo=1)

@pytest.mark.asyncio
async def test_remover_grupo_no_existe(servicio, mocks, persona_mock):
    """Restricción: El grupo debe existir."""
    mocks["repositorio"].obtener_por_id = AsyncMock(return_value=persona_mock)
    mocks["repo_grupo"].obtener_grupo_por_id = AsyncMock(return_value=None)

    with pytest.raises(GrupoNoEncontrado):
        await servicio.remover_persona_grupo_retorno(pe_codigo=1, gr_codigo=999)

@pytest.mark.asyncio
async def test_remover_persona_no_pertenece_a_grupo(servicio, mocks, persona_mock, grupo_mock):
    """Restricción: La persona debe pertenecer al grupo."""
    mocks["repositorio"].obtener_por_id = AsyncMock(return_value=persona_mock)
    mocks["repo_grupo"].obtener_grupo_por_id = AsyncMock(return_value=grupo_mock)
    mocks["repositorio"].persona_esta_en_grupo = AsyncMock(return_value=False)

    with pytest.raises(HTTPException) as exc:
        await servicio.remover_persona_grupo_retorno(pe_codigo=1, gr_codigo=1)

    assert exc.value.status_code == 400
    assert "no pertenece" in exc.value.detail.lower()