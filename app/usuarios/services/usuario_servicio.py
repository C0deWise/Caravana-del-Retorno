"""
    usuario_servicio.py contiene la lógica de negocio para la gestión de usuarios.
"""

from passlib.context import CryptContext

from app.usuarios.models.usuario import Usuario
from app.usuarios.repository.parentesco_repositorio import ParentescoRepositorio
from app.usuarios.repository.usuario_repositorio import UsuarioRepositorio
from app.usuarios.schemas.usuario_esquemas import UsuarioCrear
from app.usuarios.schemas.parentesco_esquemas import ParentescoCrear

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UsuarioServicio:

    def __init__(self, repositorio: UsuarioRepositorio, repositorio_parentesco: ParentescoRepositorio) -> None:
        self.repositorio = repositorio
        self.repositorio_parentesco = repositorio_parentesco

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
    
    async def existe_parentesco(self, codigo_solicitante: int, codigo_destinatario: int) -> bool:
        """Verifica si ya existe una relación de parentesco entre dos usuarios."""
        return await self.repositorio_parentesco.existe_parentesco(codigo_solicitante, codigo_destinatario)

    async def existe_solicitud_parentesco(self, codigo_solicitante: int, codigo_destinatario: int) -> bool:
        """Verifica si ya existe una solicitud de parentesco entre dos usuarios."""
        return await self.repositorio_parentesco.existe_solicitud_parentesco(codigo_solicitante, codigo_destinatario)
    
    async def solicitar_parentesco(self, parentesco_crear: ParentescoCrear):
        """Solicita un parentesco entre dos usuarios."""
        if parentesco_crear.codigo_solicitante == parentesco_crear.codigo_destinatario:
            raise ValueError("El solicitante y el destinatario no pueden ser el mismo usuario.")
        # Verificar que ambos usuarios existan
        if not await self.existe_usuario("us_codigo", parentesco_crear.codigo_solicitante):
            raise ValueError("El usuario solicitante no existe.")
        if not await self.existe_usuario("us_codigo", parentesco_crear.codigo_destinatario):
            raise ValueError("El usuario destinatario no existe.")
        
        if await self.existe_parentesco(parentesco_crear.codigo_solicitante, parentesco_crear.codigo_destinatario):
            raise ValueError("Ya existe una relación de parentesco entre estos usuarios.")
        if await self.existe_solicitud_parentesco(parentesco_crear.codigo_solicitante, parentesco_crear.codigo_destinatario):
            raise ValueError("Ya existe una solicitud de parentesco pendiente entre estos usuarios.")

        return await self.repositorio_parentesco.solicitar_parentesco(parentesco_crear)
    
    async def listar_parentescos_usuario(self, codigo_usuario: int):
        """Lista todas las relaciones de parentesco de un usuario."""
        return await self.repositorio_parentesco.listar_parentescos_usuario(codigo_usuario)