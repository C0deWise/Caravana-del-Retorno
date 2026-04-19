"""
    solicitud_grupo_retorno_repositorio.py Repositorio para manejar las operaciones de las solicitudes de grupos de retorno a usuarios.
"""



from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import datetime

class SolicitudGrupoRetornoRepositorio:

        def __init__(self,db: AsyncSession):
            self.db = db
    
        async def crear_solicitud_grupo_retorno(self, datos):
            pass

        async def rechazar_solicitud_grupo_retorno(self, solicitud_id: int):
            pass

        async def aceptar_solicitud_grupo_retorno(self, solicitud_id: int):
            pass

        async def obtener_solicitudes_por_grupo_retorno(self, grupo_retorno_id: int):
            pass