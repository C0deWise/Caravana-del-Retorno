
"""
colonia_reporte_repositorio.py
=============================
Propósito: Repositorio de datos para obtener información de colonias y retornos.
          Consulta datos de colonias, sus líderes y retornos asociados
          necesarios para la generación de reportes.
"""

from sqlalchemy import select

from app.colonias.models.colonia_model import Colonia
from app.retornos.modelos.retorno_modelo import Retorno
from app.usuarios.models.usuario import Usuario


class ColoniaReporteRepositorio:
    def __init__(self, db):
        self.db = db
    
    async def obtener_lider_colonia(self, co_codigo: int):
        result = await self.db.execute(
            select(Usuario)
            .where(Usuario.co_codigo == co_codigo, Usuario.ro_codigo == 2)
        )
        return result.scalars().first()
    
    async def obtener_colonias(self):
        result = await self.db.execute(
            select(Colonia).distinct()
        )
        return result.scalars().all()
    
    async def obtener_colonia(self, co_codigo: int):
        result = await self.db.execute(
            select(Colonia)
            .where(Colonia.co_codigo == co_codigo)
        )
        return result.scalars().first()
    
    async def obtener_retorno(self, re_codigo: int):
        result = await self.db.execute(
            select(Retorno)
            .where(Retorno.codigo == re_codigo)
        )
        return result.scalars().first()
