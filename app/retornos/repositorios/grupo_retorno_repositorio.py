"""
    grupo_retorno_repositorio.py define el repositorio para el modelo GrupoRetorno. Este repositorio contiene los métodos necesarios
    para la gestion de grupos de retorno.
"""


from sqlalchemy.ext.asyncio import AsyncSession

from app.retornos.esquemas.grupo_retorno_esquema import GrupoRetornoCrear

class GrupoRetornoRepositorio:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def crear_grupo_retorno(self, datos: GrupoRetornoCrear):
        pass

    