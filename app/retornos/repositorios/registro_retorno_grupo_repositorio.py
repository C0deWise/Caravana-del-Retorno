"""
    registro_retorno_grupo_repositorio.py Repositorio para gestionar los registros de grupos de retorno.
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.retornos.modelos.grupo_retorno_modelo import GrupoRetorno
from app.retornos.modelos.registro_retorno_grupo_modelo import RegistroRetornoGrupo
from app.retornos.esquemas.registro_retorno_grupo_esquema import RegistroRetornoGrupoCrear


class RegistroRetornoGrupoRepositorio:
    def __init__(self,db: AsyncSession):
        self.db = db

    async def crear_registro_grupo_retorno(self, datos: RegistroRetornoGrupoCrear) -> RegistroRetornoGrupo:
        """Crea un nuevo registro de un grupo en un retorno."""
        nuevo_registro = RegistroRetornoGrupo(
            cod_grupo=datos.cod_grupo,
            retorno=datos.retorno,
            num_hospedaje=datos.num_hospedaje,
            num_transporte=datos.num_transporte,
            num_parqueadero_carro=datos.num_parqueadero_carro,
            num_parqueadero_moto=datos.num_parqueadero_moto,
            anotacion=datos.anotacion
        )
        self.db.add(nuevo_registro)
        await self.db.commit()
        await self.db.refresh(nuevo_registro)
        return nuevo_registro

    async def obtener_registro_por_grupo_y_retorno(self, gr_codigo: int, re_codigo: int) -> RegistroRetornoGrupo | None:
        """Verifica si un grupo ya está registrado en un retorno específico."""
        stmt = select(RegistroRetornoGrupo).where(
            RegistroRetornoGrupo.cod_grupo == gr_codigo,
            RegistroRetornoGrupo.retorno == re_codigo
        )
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def existe_lider_con_grupo_registrado_en_retorno(self, us_codigo_lider: int, re_codigo: int) -> bool:
        """Verifica si el líder ya tiene un grupo registrado en un retorno específico."""
        stmt = select(RegistroRetornoGrupo).join(
            GrupoRetorno,
            GrupoRetorno.gr_codigo == RegistroRetornoGrupo.cod_grupo
        ).where(
            GrupoRetorno.us_codigo_lider == us_codigo_lider,
            RegistroRetornoGrupo.retorno == re_codigo
        )
        result = await self.db.execute(stmt)
        return result.scalars().first() is not None