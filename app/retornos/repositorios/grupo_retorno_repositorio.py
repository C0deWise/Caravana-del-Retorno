"""
    grupo_retorno_repositorio.py define el repositorio para el modelo GrupoRetorno. Este repositorio contiene los métodos necesarios
    para la gestion de grupos de retorno.
""" 
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.retornos.esquemas.grupo_retorno_esquema import GrupoRetornoCrear
from app.retornos.modelos.grupo_retorno_modelo import GrupoRetorno
from app.usuarios.models.usuario import Usuario # Importar el modelo de Usuario para la relación

class GrupoRetornoRepositorio:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def crear_grupo_retorno(self, datos: GrupoRetornoCrear):
        """Crea un nuevo grupo de retorno en la base de datos."""
        nuevo_grupo = GrupoRetorno(
            us_codigo_lider=datos.lider
        )
        self.db.add(nuevo_grupo)
        await self.db.commit()
        await self.db.refresh(nuevo_grupo)
        return nuevo_grupo
    
    async def obtener_grupos_por_lider_id(self, us_codigo_lider: int) -> list[GrupoRetorno]:
        """Obtiene todos los grupos de retorno liderados por un usuario específico."""
        result = await self.db.execute(select(GrupoRetorno).filter(GrupoRetorno.us_codigo_lider == us_codigo_lider))
        return list(result.scalars().all())

    async def obtener_lider_por_grupo_id(self, gr_codigo: int) -> Usuario | None:
        """Obtiene el objeto Usuario que es líder de un grupo de retorno específico."""
        result = await self.db.execute(select(GrupoRetorno).filter(GrupoRetorno.gr_codigo == gr_codigo).options(selectinload(GrupoRetorno.lider)))
        grupo = result.scalars().first()
        return grupo.lider if grupo else None

    async def obtener_grupo_por_id(self, gr_codigo: int) -> GrupoRetorno | None:
        """Obtiene un grupo de retorno por su código."""
        result = await self.db.execute(select(GrupoRetorno).filter(GrupoRetorno.gr_codigo == gr_codigo))
        return result.scalars().first()
    
    async def eliminar_grupo_retorno(self, gr_codigo: int):
        """Elimina un grupo de retorno por su código con eliminación en cascada.
        
        Esto eliminará automáticamente:
        - Todos los miembros (persona_grupo_retorno)
        - Todas las solicitudes relacionadas (SolicitudGrupoRetorno)
        - Todos los registros de retorno (RegistroRetornoGrupo)
        """
        grupo = await self.obtener_grupo_por_id(gr_codigo)
        if grupo:
            await self.db.delete(grupo)
            await self.db.commit()