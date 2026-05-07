

from sqlalchemy import select

from app.colonias.models.colonia_model import Colonia
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
