"""
    registro_retorno_grupo_repositorio.py Repositorio para gestionar los registros de grupos de retorno.
"""

from sqlalchemy.ext.asyncio import AsyncSession

from app.retornos.esquemas.registro_retorno_grupo_esquema import RegistroRetornoGrupoCrear


class RegistroRetornoGrupoRepositorio:
    def __init__(self,db: AsyncSession):
        self.db = db

    async def crear_registro_grupo_retorno(self, datos: RegistroRetornoGrupoCrear):
        pass