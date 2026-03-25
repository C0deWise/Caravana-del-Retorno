import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import date
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from app.usuarios.schemas.usuario_esquemas import UsuarioCrear
from app.usuarios.services.usuario_servicio import UsuarioServicio
from app.usuarios.models.usuario import TipoDoc, Genero


# ─────────────────────────────────────────
#  Fixtures
# ─────────────────────────────────────────
@pytest.fixture
def schema_valido():
    return UsuarioCrear(
        tipo_doc=TipoDoc.CC,
        documento="1234567890",
        celular="+57 300 123 4567",
        correo="juan.perez@gmail.com",
        contrasenia="MiContrasenia123",
        codigo_colonia=None,
        codigo_rol=1,
        nombre="Juan",
        apellido="Perez",
        genero=Genero.M,
        fecha_nacimiento=date(1995, 6, 15),
        pais="Colombia",
        departamento="Cauca",
        ciudad="Popayan",
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
        mock_repositorio.registrar.return_value = MagicMock(us_codigo=1)
        usuario = await servicio.registrar(schema_valido)
        assert usuario.us_codigo == 1
        mock_repositorio.registrar.assert_called_once()

    @pytest.mark.asyncio
    async def test_contrasenia_es_hasheada(self, servicio, mock_repositorio, schema_valido):
        mock_repositorio.registrar.return_value = MagicMock(us_codigo=1)
        contrasenia_plana = schema_valido.contrasenia
        await servicio.registrar(schema_valido)

        schema_enviado = mock_repositorio.registrar.call_args[0][0]
        assert schema_enviado.contrasenia != contrasenia_plana
        assert schema_enviado.contrasenia.startswith("$2b$")


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
            UsuarioCrear(**{**schema_valido.model_dump(), "us_correo": correo})

    @pytest.mark.parametrize("correo", [
        "usuario@gmail.com",
        "usuario.apellido@empresa.co",
        "usuario+tag@dominio.com",
        "usuario@sub.dominio.com",
    ])
    def test_correo_valido(self, schema_valido, correo):
        schema = UsuarioCrear(**{**schema_valido.model_dump(), "us_correo": correo})
        assert schema.correo == correo


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
            UsuarioCrear(**{**schema_valido.model_dump(), "us_celular": celular})

    @pytest.mark.parametrize("celular", [
        "+57 300 123 4567",
        "3001234567",
        "+1 800 555 0199",
    ])
    def test_celular_valido(self, schema_valido, celular):
        schema = UsuarioCrear(**{**schema_valido.model_dump(), "us_celular": celular})
        assert schema.celular == celular


# ─────────────────────────────────────────
#  Validación de enums
# ─────────────────────────────────────────
class TestEnums:

    @pytest.mark.parametrize("tipo_doc", ["XX", "PA", "NIT", "", "cc"])
    def test_tipo_doc_invalido(self, schema_valido, tipo_doc):
        with pytest.raises(ValueError):
            UsuarioCrear(**{**schema_valido.model_dump(), "us_tipo_doc": tipo_doc})

    @pytest.mark.parametrize("tipo_doc", ["CC", "CE"])
    def test_tipo_doc_valido(self, schema_valido, tipo_doc):
        schema = UsuarioCrear(**{**schema_valido.model_dump(), "us_tipo_doc": tipo_doc})
        assert schema.tipo_doc == tipo_doc

    @pytest.mark.parametrize("genero", ["X", "male", "female", "", "f"])
    def test_genero_invalido(self, schema_valido, genero):
        with pytest.raises(ValueError):
            UsuarioCrear(**{**schema_valido.model_dump(), "us_genero": genero})

    @pytest.mark.parametrize("genero", ["F", "M", "otro"])
    def test_genero_valido(self, schema_valido, genero):
        schema = UsuarioCrear(**{**schema_valido.model_dump(), "us_genero": genero})
        assert schema.genero == genero