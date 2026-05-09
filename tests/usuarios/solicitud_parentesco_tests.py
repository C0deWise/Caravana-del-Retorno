"""
    test_solicitar_parentesco.py contiene las pruebas unitarias para el método
    solicitar_parentesco del servicio UsuarioServicio.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from app.usuarios.services.usuario_servicio import UsuarioServicio
from app.usuarios.schemas.parentesco_esquemas import ParentescoCrear


# ─── Fixture base ────────────────────────────────────────────────────────────

@pytest.fixture
def repositorio():
    """Mock del repositorio de usuarios."""
    repo = MagicMock()
    repo.existe_usuario = AsyncMock(return_value=False)
    return repo


@pytest.fixture
def repositorio_parentesco():
    """Mock del repositorio de parentesco."""
    repo = MagicMock()
    repo.existe_parentesco = AsyncMock(return_value=False)
    repo.existe_solicitud_parentesco = AsyncMock(return_value=False)
    repo.solicitar_parentesco = AsyncMock(return_value={"mensaje": "Solicitud creada exitosamente."})
    return repo


@pytest.fixture
def servicio(repositorio, repositorio_parentesco):
    """Instancia de UsuarioServicio con repositorios mockeados."""
    return UsuarioServicio(
        repositorio=repositorio,
        repositorio_parentesco=repositorio_parentesco,
    )


@pytest.fixture
def parentesco_crear():
    """Schema válido de solicitud de parentesco."""
    return ParentescoCrear(
        codigo_solicitante=1,
        codigo_destinatario=2,
        tipo_parentesco="hermano (a)",
    )


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
async def test_solicitar_parentesco_exitoso(servicio, repositorio, repositorio_parentesco, parentesco_crear):
    """La solicitud se crea correctamente cuando todos los datos son válidos."""
    configurar_existe_usuario(repositorio, solicitante=True, destinatario=True)

    resultado = await servicio.solicitar_parentesco(parentesco_crear)

    assert resultado == {"mensaje": "Solicitud creada exitosamente."}
    repositorio_parentesco.solicitar_parentesco.assert_awaited_once_with(parentesco_crear)


@pytest.mark.asyncio
async def test_solicitar_parentesco_mismo_usuario(servicio):
    """Lanza ValueError cuando el solicitante y el destinatario son el mismo usuario."""
    parentesco_mismo_usuario = ParentescoCrear(
        codigo_solicitante=1,
        codigo_destinatario=1,
        tipo_parentesco="hermano (a)",
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