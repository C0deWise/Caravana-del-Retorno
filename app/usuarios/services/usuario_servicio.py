from passlib.context import CryptContext

from app.usuarios.models.usuario import Usuario
from app.usuarios.repository.usuario_repositorio import UsuarioRepositorio
from app.usuarios.schemas.usuario_esquemas import UsuarioCrear


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UsuarioServicio:

    def __init__(self, repositorio: UsuarioRepositorio) -> None:
        self.repositorio = repositorio

    async def registrar(self, schema: UsuarioCrear) -> Usuario:
        errores = []

        # Verificar campos únicos antes del INSERT
        if await self.existe_usuario("us_documento", schema.documento):
            errores.append("El documento ya se encuentra registrado.")
        if await self.existe_usuario("us_correo", schema.correo):
            errores.append("El correo ya se encuentra registrado.")
        if await self.existe_usuario("us_celular", schema.celular):
            errores.append("El celular ya se encuentra registrado.")

        if errores:
            raise ValueError(errores)
        """Cifra la contraseña y delega el registro al repositorio."""
        schema.contrasenia = pwd_context.hash(schema.contrasenia)
        return await self.repositorio.registrar(schema)
    
    async def existe_usuario(self, campo: str, valor: str) -> bool:
        """Verifica si un usuario con el tipo de documento y número de documento ya existe."""
        return await self.repositorio.existe_usuario(campo, valor)