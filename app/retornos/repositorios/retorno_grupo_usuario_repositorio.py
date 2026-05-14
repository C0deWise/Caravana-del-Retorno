"""
    retorno_grupo_usuario_repositorio.py define el repositorio para gestionar la asociación de usuarios a grupos de retorno.
"""

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.retornos.modelos.grupo_retorno_modelo import GrupoRetorno
from app.retornos.modelos.retorno_grupo_usuario_modelo import RetornoGrupoUsuario
from app.retornos.modelos.registro_retorno_grupo_modelo import RegistroRetornoGrupo
from app.usuarios.models.usuario import Usuario
from sqlalchemy.orm import selectinload
class RetornoGrupoUsuarioRepositorio:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def asociar_usuario_a_grupo_retorno(self, usuario_id: int, grupo_retorno_id: int):
        """Asocia un usuario a un grupo de retorno específico."""
        asociacion = RetornoGrupoUsuario(us_codigo=usuario_id, gr_codigo=grupo_retorno_id)
        self.db.add(asociacion)
        await self.db.commit()
        await self.db.refresh(asociacion)
        return asociacion

    async def darse_de_baja_de_grupo_retorno(self, usuario_id: int, grupo_retorno_id: int):
        """Permite a un usuario darse de baja de un grupo de retorno específico."""
        # Aquí se implementaría la lógica para eliminar la asociación entre el usuario y el grupo de retorno en la base de datos.
        pass

    async def existe_usuario_en_grupo_para_retorno(self, us_codigo: int, re_codigo: int) -> bool:
        """
        Verifica si un usuario ya está en la tabla usuario_grupo_retorno 
        vinculada a un grupo que ya tiene un registro para el retorno dado.
        """
        stmt = select(RetornoGrupoUsuario).join(
            RegistroRetornoGrupo, RetornoGrupoUsuario.gr_codigo == RegistroRetornoGrupo.cod_grupo
        ).where(
            RetornoGrupoUsuario.us_codigo == us_codigo,
            RegistroRetornoGrupo.retorno == re_codigo
        )
        result = await self.db.execute(stmt)
        return result.scalars().first() is not None

    async def obtener_miembros_por_grupo(self, gr_codigo: int) -> list[Usuario]:
        """Obtiene la lista de usuarios que pertenecen a un grupo de retorno."""
        stmt = select(Usuario).join(RetornoGrupoUsuario).where(RetornoGrupoUsuario.gr_codigo == gr_codigo)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def contar_miembros_adicionales(self, gr_codigo: int) -> int:
        """Cuenta cuántos miembros tiene el grupo (sin contar al líder)."""
        stmt = select(func.count(RetornoGrupoUsuario.ugr_codigo)).where(
            RetornoGrupoUsuario.gr_codigo == gr_codigo
        )
        result = await self.db.execute(stmt)
        return result.scalar() or 0
    
    

    async def obtener_grupo_por_usuario_retorno(self, usuario_id: int, retorno_id: int):
        """Obtiene el grupo de retorno al que pertenece un usuario específico para un retorno dado."""
        stmt = (select(RetornoGrupoUsuario)
            .options(selectinload(RetornoGrupoUsuario.grupo))
            .join(RegistroRetornoGrupo, RetornoGrupoUsuario.gr_codigo == RegistroRetornoGrupo.cod_grupo)
            .where(
                RetornoGrupoUsuario.us_codigo == usuario_id,
                RegistroRetornoGrupo.retorno == retorno_id
            )
        )
        result = await self.db.execute(stmt)
        retorno_grupo_usuario = result.scalars().first()
        return retorno_grupo_usuario.grupo if retorno_grupo_usuario else None
       