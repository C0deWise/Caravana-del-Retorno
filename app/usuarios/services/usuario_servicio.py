"""
Este módulo contiene la lógica de negocio para la gestión de usuarios.
Se encarga de orquestar las operaciones, validaciones y transformaciones
de datos requeridas antes de interactuar con la capa de repositorio.
"""

from passlib.context import CryptContext

from app.usuarios.models.usuario import Usuario
from app.usuarios.repository.usuario_repositorio import UsuarioRepositorio
from app.usuarios.schemas.usuario_esquemas import UsuarioCrear


# Contexto para el cifrado y verificación de contraseñas utilizando el algoritmo bcrypt.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UsuarioServicio:
    """
    Servicio para gestionar la lógica de negocio de los usuarios.
    """

    def __init__(self, repositorio: UsuarioRepositorio) -> None:
        """
        Inicializa el servicio con un repositorio de usuarios.

        Args:
            repositorio (UsuarioRepositorio): El repositorio para el acceso a datos.
        """
        self.repositorio = repositorio

    async def registrar(self, schema: UsuarioCrear) -> Usuario:
        """
        Registra un nuevo usuario en el sistema.

        Este método realiza validaciones de negocio, como la verificación de campos únicos,
        cifra la contraseña y luego delega la creación del usuario al repositorio.

        Args:
            schema (UsuarioCrear): Los datos del usuario a registrar.

        Returns:
            Usuario: El objeto del usuario recién creado.

        Raises:
            ValueError: Si se detectan violaciones de campos únicos (documento, correo, celular).
        """
        errores = []

        # Se realizan verificaciones de unicidad para evitar errores de integridad en la BD.
        # Esto permite devolver un mensaje de error claro y específico al cliente.
        if await self.repositorio.existe_usuario("us_documento", schema.documento):
            errores.append("El documento ya se encuentra registrado.")
        if await self.repositorio.existe_usuario("us_correo", schema.correo):
            errores.append("El correo ya se encuentra registrado.")
        if await self.repositorio.existe_usuario("us_celular", schema.celular):
            errores.append("El celular ya se encuentra registrado.")

        # Si se encontraron errores, se lanzan en una sola excepción.
        if errores:
            raise ValueError(". ".join(errores))

        # Cifrado de la contraseña antes de almacenarla en la base de datos.
        schema.contrasenia = pwd_context.hash(schema.contrasenia)

        return await self.repositorio.registrar(schema)

    async def obtener_todos(self) -> list[Usuario]:
        """
        Recupera todos los usuarios registrados en el sistema.

        Returns:
            list[Usuario]: Una lista de todos los usuarios.
        """
        return await self.repositorio.obtener_todos()

    async def buscar_por_nombre(self, nombre: str) -> list[Usuario]:
        """
        Busca usuarios por su nombre.

        Args:
            nombre (str): El término de búsqueda para el nombre.

        Returns:
            list[Usuario]: Una lista de usuarios que coinciden con el nombre.
        """
        return await self.repositorio.buscar_por_nombre(nombre)

    async def buscar_por_documento(self, documento: str) -> Usuario | None:
        """
        Busca un usuario específico por su número de documento.

        Args:
            documento (str): El número de documento a buscar.

        Returns:
            Usuario | None: El usuario encontrado o None si no existe.
        """
        return await self.repositorio.buscar_por_documento(documento)

    async def existe_usuario(self, campo: str, valor: str) -> bool:
        """
        Verifica si un usuario ya existe basado en un campo y valor específicos.
        Delega la llamada directamente al repositorio.

        Args:
            campo (str): El nombre del campo a verificar (ej. 'us_documento').
            valor (str): El valor a buscar en ese campo.

        Returns:
            bool: True si el usuario existe, False de lo contrario.
        """
        return await self.repositorio.existe_usuario(campo, valor)