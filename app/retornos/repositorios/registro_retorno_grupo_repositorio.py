"""
    registro_retorno_grupo_repositorio.py Repositorio para gestionar los registros de grupos de retorno.
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.retornos.modelos.registro_retorno_grupo_modelo import RegistroRetornoGrupo
from app.retornos.esquemas.registro_retorno_grupo_esquema import RegistroRetornoGrupoCrear


class RegistroRetornoGrupoRepositorio:
    def __init__(self,db: AsyncSession):
        self.db = db

    async def crear_registro_grupo_retorno(self, datos: RegistroRetornoGrupoCrear) -> RegistroRetornoGrupo:
        """Crea un nuevo registro de un grupo en un retorno."""
        nuevo_registro = RegistroRetornoGrupo(
            gr_codigo=datos.cod_grupo,
            re_codigo=datos.retorno,
            reggr_num_hospedaje=datos.num_hospedaje,
            reggr_num_transporte=datos.num_transporte,
            reggr_num_parqueadero=datos.num_parqueadero,
            reggr_anotacion=datos.anotacion
        )
        self.db.add(nuevo_registro)
        await self.db.commit()
        await self.db.refresh(nuevo_registro)
        return nuevo_registro

    async def obtener_registro_por_grupo_y_retorno(self, gr_codigo: int, re_codigo: int) -> RegistroRetornoGrupo | None:
        """Verifica si un grupo ya está registrado en un retorno específico."""
        stmt = select(RegistroRetornoGrupo).where(
            RegistroRetornoGrupo.gr_codigo == gr_codigo,
            RegistroRetornoGrupo.re_codigo == re_codigo
        )
        result = await self.db.execute(stmt)
        return result.scalars().first()