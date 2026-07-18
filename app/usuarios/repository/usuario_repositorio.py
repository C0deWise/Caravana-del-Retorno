"""
Este módulo contiene la capa de acceso a datos para la entidad `Usuario`.
Se encarga de las operaciones de base de datos (CRUD) y otras consultas
específicas para los usuarios, interactuando directamente con el modelo SQLAlchemy.
"""

from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from app.usuarios.models.password_recovery_token import PasswordRecoveryToken
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

    async def revocar_tokens_recuperacion_activos(self, us_codigo: int) -> None:
        result = await self.db.execute(
            select(PasswordRecoveryToken).where(
                PasswordRecoveryToken.us_codigo == us_codigo,
                PasswordRecoveryToken.prt_revocado.is_(False),
                PasswordRecoveryToken.prt_used_at.is_(None),
            )
        )
        ahora = datetime.now(timezone.utc)
        for token in result.scalars().all():
            token.prt_revocado = True
            if token.prt_expires_at <= ahora:
                token.prt_used_at = ahora
        await self.db.commit()

    async def crear_token_recuperacion(
        self,
        us_codigo: int,
        jti_hash: str,
        expires_at: datetime,
    ) -> PasswordRecoveryToken:
        token = PasswordRecoveryToken(
            us_codigo=us_codigo,
            prt_jti_hash=jti_hash,
            prt_expires_at=expires_at,
        )
        self.db.add(token)
        await self.db.commit()
        await self.db.refresh(token)
        return token

    async def obtener_token_recuperacion_activo(
        self,
        us_codigo: int,
        jti_hash: str,
    ) -> PasswordRecoveryToken | None:
        ahora = datetime.now(timezone.utc)
        result = await self.db.execute(
            select(PasswordRecoveryToken).where(
                PasswordRecoveryToken.us_codigo == us_codigo,
                PasswordRecoveryToken.prt_jti_hash == jti_hash,
                PasswordRecoveryToken.prt_revocado.is_(False),
                PasswordRecoveryToken.prt_used_at.is_(None),
                PasswordRecoveryToken.prt_expires_at >= ahora,
            )
        )
        return result.scalar_one_or_none()

    async def actualizar_contrasenia_con_token(
        self,
        usuario: Usuario,
        nueva_contrasenia_hash: str,
        token_recuperacion: PasswordRecoveryToken,
    ) -> None:
        usuario.us_contrasenia = nueva_contrasenia_hash
        token_recuperacion.prt_used_at = datetime.now(timezone.utc)
        token_recuperacion.prt_revocado = True
        await self.db.commit()

    async def buscar_por_google_id(self, google_id: str) -> Usuario | None:
        """
        Busca un usuario por su Google ID.

        Args:
            google_id: El ID único de Google del usuario.

        Returns:
            Usuario | None: El usuario encontrado o None si no existe.
        """
        result = await self.db.execute(
            select(Usuario).where(Usuario.us_google_id == google_id)
        )
        return result.scalar_one_or_none()