from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select

from app.usuarios.models.usuario import Usuario
from app.usuarios.schemas.usuario_esquemas import UsuarioCrear


class UsuarioRepositorio:

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def registrar(self, schema: UsuarioCrear) -> Usuario:

        usuario = Usuario(us_tipo_doc=schema.tipo_doc, us_documento=schema.documento, us_celular=schema.celular,
                          co_codigo=schema.codigo_colonia, ro_codigo=schema.codigo_rol, us_nombre=schema.nombre,
                          us_apellido=schema.apellido, us_genero=schema.genero, us_fecha_nacimiento=schema.fecha_nacimiento,
                          us_pais=schema.pais, us_departamento=schema.departamento, us_ciudad=schema.ciudad,
                          us_correo=schema.correo, us_contrasenia=schema.contrasenia)
        self.db.add(usuario)
        await self.db.commit()
        await self.db.refresh(usuario)
        return usuario


    async def existe_usuario(self, campo: str, valor: str) -> bool:
        """Verifica si existe un usuario con el valor especificado en el campo dado."""
        result = await self.db.execute(
            select(Usuario).where(getattr(Usuario, campo) == valor)
        )
        return result.scalar_one_or_none() is not None