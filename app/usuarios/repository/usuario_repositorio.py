"""
Este módulo contiene la capa de acceso a datos para la entidad `Usuario`.
Se encarga de las operaciones de base de datos (CRUD) y otras consultas
específicas para los usuarios, interactuando directamente con el modelo SQLAlchemy.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from app.usuarios.models.usuario import Usuario
from app.usuarios.schemas.usuario_esquemas import UsuarioCrear


class UsuarioRepositorio:
    """
    Repositorio para gestionar las operaciones de base de datos de los usuarios.
    """

    def __init__(self, db: AsyncSession) -> None:
        """
        Inicializa el repositorio con una sesión de base de datos.

        Args:
            db (AsyncSession): Sesión de base de datos asíncrona.
        """
        self.db = db

    async def registrar(self, schema: UsuarioCrear) -> Usuario:
        """
        Crea un nuevo registro de usuario en la base de datos.

        Args:
            schema (UsuarioCrear): Datos del usuario a crear.

        Returns:
            Usuario: El objeto de usuario recién creado.

        Raises:
            IntegrityError: Si se viola una restricción de unicidad (ej. documento, correo).
        """
        usuario = Usuario(
            us_tipo_doc=schema.tipo_doc,
            us_documento=schema.documento,
            us_celular=schema.celular,
            co_codigo=schema.codigo_colonia,
            ro_codigo=schema.codigo_rol,
            us_nombre=schema.nombre,
            us_apellido=schema.apellido,
            us_genero=schema.genero,
            us_fecha_nacimiento=schema.fecha_nacimiento,
            us_pais=schema.pais,
            us_departamento=schema.departamento,
            us_ciudad=schema.ciudad,
            us_correo=schema.correo,
            us_contrasenia=schema.contrasenia
        )
        self.db.add(usuario)
        await self.db.commit()
        await self.db.refresh(usuario)
        return usuario

    async def obtener_todos(self) -> list[Usuario]:
        """
        Obtiene todos los usuarios registrados en el sistema.

        Returns:
            list[Usuario]: Una lista de todos los usuarios.
        """
        result = await self.db.execute(select(Usuario))
        return list(result.scalars().all())

    async def buscar_por_nombre(self, nombre: str) -> list[Usuario]:
        """
        Busca usuarios cuyo nombre coincida parcialmente con el término de búsqueda.
        La búsqueda no es sensible a mayúsculas y minúsculas.

        Args:
            nombre (str): El nombre o parte del nombre a buscar.

        Returns:
            list[Usuario]: Lista de usuarios que coinciden con el criterio.
        """
        result = await self.db.execute(
            select(Usuario).where(Usuario.us_nombre.ilike(f"%{nombre}%"))
        )
        return list(result.scalars().all())

    async def buscar_por_documento(self, documento: str) -> Usuario | None:
        """
        Busca un usuario por su número de documento exacto.

        Args:
            documento (str): Número de documento a buscar.

        Returns:
            Usuario | None: El usuario encontrado o None si no existe.
        """
        result = await self.db.execute(
            select(Usuario).where(Usuario.us_documento == documento)
        )
        return result.scalar_one_or_none()

    async def buscar_por_correo(self, correo: str) -> Usuario | None:
        """
        Busca un usuario por su correo exacto.

        Args:
            correo (str): Correo a buscar.

        Returns:
            Usuario | None: El usuario encontrado o None si no existe.
        """
        result = await self.db.execute(
            select(Usuario).where(Usuario.us_correo == correo)
        )
        return result.scalar_one_or_none()
      
    async def obtener_usuario_por_id(self, us_id: int) -> Usuario | None:
        """Obtiene un usuario por su ID."""
        resultado = await self.db.execute(
            select(Usuario).where(Usuario.us_codigo == us_id).options(joinedload(Usuario.colonia))
        )
        return resultado.scalar_one_or_none()

    async def existe_usuario(self, campo: str, valor: str) -> bool:
        """
        Verifica si ya existe un usuario con un valor específico en un campo determinado.
        Útil para validar campos únicos como 'us_documento', 'us_correo', etc.

        Args:
            campo (str): El nombre del atributo del modelo Usuario a verificar.
            valor (str): El valor a buscar en dicho campo.

        Returns:
            bool: True si el usuario existe, False en caso contrario.
        """
        result = await self.db.execute(
            select(Usuario).where(getattr(Usuario, campo) == valor)
        )
        return result.scalar_one_or_none() is not None

    async def buscar_por_colonia(self, colonia: int) -> list[Usuario]:
        """
        Busca usuarios miembros por su código de colonia.

        Args:
            colonia (int): El código de la colonia a buscar.

        Returns:
            list[Usuario]: Lista de usuarios que pertenecen a la colonia especificada.
        """
        result = await self.db.execute(
            select(Usuario).where(Usuario.co_codigo == colonia)
        )
        return list(result.scalars().all())