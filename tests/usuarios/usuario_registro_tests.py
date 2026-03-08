import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import date
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from app.usuarios.schemas.usuario_esquemas import UsuarioSchema
from app.usuarios.services.usuario_servicio import UsuarioServicio
from app.usuarios.models.usuario import TipoDoc, Genero


# ─────────────────────────────────────────
#  Fixtures
# ─────────────────────────────────────────
@pytest.fixture
def schema_valido():
    return UsuarioSchema(
        us_tipo_doc=TipoDoc.CC,
        us_documento="1234567890",
        us_celular="+57 300 123 4567",
        us_correo="juan.perez@gmail.com",
        us_contrasenia="MiContrasenia123",
        co_codigo=None,
        ro_codigo=1,
        us_nombre="Juan",
        us_apellido="Perez",
        us_genero=Genero.M,
        us_fecha_nacimiento=date(1995, 6, 15),
        us_pais="Colombia",
        us_departamento="Cauca",
        us_ciudad="Popayan",
    )


@pytest.fixture
def mock_repositorio():
    repositorio = MagicMock()
    repositorio.registrar = AsyncMock()
    return repositorio


@pytest.fixture
def servicio(mock_repositorio):
    return UsuarioServicio(mock_repositorio)


# ─────────────────────────────────────────
#  Servicio — registro exitoso
# ─────────────────────────────────────────
class TestRegistrar:

    @pytest.mark.asyncio
    async def test_registrar_exitoso(self, servicio, mock_repositorio, schema_valido):
        mock_repositorio.registrar.return_value = MagicMock(id=1)
        usuario = await servicio.registrar(schema_valido)
        assert usuario.id == 1
        mock_repositorio.registrar.assert_called_once()

    @pytest.mark.asyncio
    async def test_contrasenia_es_hasheada(self, servicio, mock_repositorio, schema_valido):
        mock_repositorio.registrar.return_value = MagicMock(id=1)
        contrasenia_plana = schema_valido.us_contrasenia
        await servicio.registrar(schema_valido)

        schema_enviado = mock_repositorio.registrar.call_args[0][0]
        assert schema_enviado.us_contrasenia != contrasenia_plana
        assert schema_enviado.us_contrasenia.startswith("$2b$")


# ─────────────────────────────────────────
#  Violaciones de integridad
# ─────────────────────────────────────────
class TestIntegridad:

    @pytest.mark.asyncio
    async def test_documento_duplicado(self, servicio, mock_repositorio, schema_valido):
        mock_repositorio.registrar.side_effect = ValueError("El documento ya se encuentra registrado.")
        with pytest.raises(ValueError, match="documento"):
            await servicio.registrar(schema_valido)

    @pytest.mark.asyncio
    async def test_correo_duplicado(self, servicio, mock_repositorio, schema_valido):
        mock_repositorio.registrar.side_effect = ValueError("El correo ya se encuentra registrado.")
        with pytest.raises(ValueError, match="correo"):
            await servicio.registrar(schema_valido)

    @pytest.mark.asyncio
    async def test_celular_duplicado(self, servicio, mock_repositorio, schema_valido):
        mock_repositorio.registrar.side_effect = ValueError("El celular ya se encuentra registrado.")
        with pytest.raises(ValueError, match="celular"):
            await servicio.registrar(schema_valido)


# ─────────────────────────────────────────
#  Validación de correo
# ─────────────────────────────────────────
class TestCorreo:

    @pytest.mark.parametrize("correo", [
        "noesuncorreo",
        "sin_arroba.com",
        "@sinlocal.com",
        "sin_extension@dominio",
        "espacios en@correo.com",
        "",
    ])
    def test_correo_invalido(self, schema_valido, correo):
        with pytest.raises(ValueError):
            schema_valido.model_copy(update={"us_correo": correo})
            UsuarioSchema(**{**schema_valido.model_dump(), "us_correo": correo})

    @pytest.mark.parametrize("correo", [
        "usuario@gmail.com",
        "usuario.apellido@empresa.co",
        "usuario+tag@dominio.com",
        "usuario@sub.dominio.com",
    ])
    def test_correo_valido(self, schema_valido, correo):
        schema = UsuarioSchema(**{**schema_valido.model_dump(), "us_correo": correo})
        assert schema.us_correo == correo


# ─────────────────────────────────────────
#  Validación de celular
# ─────────────────────────────────────────
class TestCelular:

    @pytest.mark.parametrize("celular", [
        "abc123",
        "123",
        "1234567890123456",
        "++57300",
        "300 abc 1234",
    ])
    def test_celular_invalido(self, schema_valido, celular):
        with pytest.raises(ValueError):
            UsuarioSchema(**{**schema_valido.model_dump(), "us_celular": celular})

    @pytest.mark.parametrize("celular", [
        "+57 300 123 4567",
        "3001234567",
        "+1 800 555 0199",
    ])
    def test_celular_valido(self, schema_valido, celular):
        schema = UsuarioSchema(**{**schema_valido.model_dump(), "us_celular": celular})
        assert schema.us_celular == celular


# ─────────────────────────────────────────
#  Validación de enums
# ─────────────────────────────────────────
class TestEnums:

    @pytest.mark.parametrize("tipo_doc", ["XX", "PA", "NIT", "", "cc"])
    def test_tipo_doc_invalido(self, schema_valido, tipo_doc):
        with pytest.raises(ValueError):
            UsuarioSchema(**{**schema_valido.model_dump(), "us_tipo_doc": tipo_doc})

    @pytest.mark.parametrize("tipo_doc", ["CC", "CE"])
    def test_tipo_doc_valido(self, schema_valido, tipo_doc):
        schema = UsuarioSchema(**{**schema_valido.model_dump(), "us_tipo_doc": tipo_doc})
        assert schema.us_tipo_doc == tipo_doc

    @pytest.mark.parametrize("genero", ["X", "male", "female", "", "f"])
    def test_genero_invalido(self, schema_valido, genero):
        with pytest.raises(ValueError):
            UsuarioSchema(**{**schema_valido.model_dump(), "us_genero": genero})

    @pytest.mark.parametrize("genero", ["F", "M", "otro"])
    def test_genero_valido(self, schema_valido, genero):
        schema = UsuarioSchema(**{**schema_valido.model_dump(), "us_genero": genero})
        assert schema.us_genero == genero