from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select

from app.usuarios.models.usuario import Usuario
from app.usuarios.schemas.usuario_esquemas import UsuarioSchema


class UsuarioRepositorio:

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def registrar(self, schema: UsuarioSchema) -> Usuario:
        errores = []

        # Verificar campos únicos antes del INSERT
        if await self._existe("us_documento", schema.us_documento):
            errores.append("El documento ya se encuentra registrado.")
        if await self._existe("us_correo", schema.us_correo):
            errores.append("El correo ya se encuentra registrado.")
        if await self._existe("us_celular", schema.us_celular):
            errores.append("El celular ya se encuentra registrado.")

        if errores:
            raise ValueError(errores)

        usuario = Usuario(**schema.model_dump())
        self.db.add(usuario)
        await self.db.commit()
        await self.db.refresh(usuario)
        return usuario

    async def obtener_usuario_por_id(self, us_id: int) -> Usuario | None:
        """Obtiene un usuario por su ID."""
        resultado = await self.db.execute(
            select(Usuario).where(Usuario.us_codigo == us_id)
        )
        return resultado.scalar_one_or_none()

    async def _existe(self, campo: str, valor: str) -> bool:
        """Verifica si un valor ya existe en la columna indicada."""
        result = await self.db.execute(
            select(Usuario).where(getattr(Usuario, campo) == valor)
        )
        return result.scalar_one_or_none() is not None