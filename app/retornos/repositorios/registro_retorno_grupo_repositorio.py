

from sqlalchemy.ext.asyncio import AsyncSession

from app.retornos.esquemas.registro_retorno_grupo_esquema import RegistroRetornoGrupoCrear


class RegistroRetornoGrupoRepositorio:
    def __init__(self,db: AsyncSession):
        self.db = db

    async def crear_grupo_retorno(self, datos: RegistroRetornoGrupoCrear):
        pass