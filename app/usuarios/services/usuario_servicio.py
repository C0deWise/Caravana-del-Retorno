"""
    usuario_servicio.py contiene la lógica de negocio para la gestión de usuarios.
"""

from passlib.context import CryptContext

from app.usuarios.models.usuario import Usuario
from app.usuarios.repository.usuario_repositorio import UsuarioRepositorio
from app.usuarios.schemas.usuario_esquemas import UsuarioSchema


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UsuarioServicio:

    def __init__(self, repositorio: UsuarioRepositorio) -> None:
        self.repositorio = repositorio

    async def registrar(self, schema: UsuarioSchema) -> Usuario:
        """Cifra la contraseña y delega el registro al repositorio."""
        schema.us_contrasenia = pwd_context.hash(schema.us_contrasenia)
        return await self.repositorio.registrar(schema)