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
    
    async def obtener_usuario_por_id(self, us_id: int) -> Usuario | None:
        """Obtiene un usuario por su ID."""
        return await self.repositorio.obtener_usuario_por_id(us_id)