from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.multimedia.modelos.multimedia_modelo import Multimedia
from app.multimedia.esquemas.multimedia_esquemas import MultimediaCrear

class MultimediaRepositorio:
    def __init__(self, db:AsyncSession):
        self.db = db

    async def crear_multimedia(self, data:MultimediaCrear) -> Multimedia:
        nuevo_multimedia = Multimedia(
            retorno=data.retorno,
            tipo=data.tipo,
            url=data.url,
            nombre_archivo=data.nombre_archivo
        )
        self.db.add(nuevo_multimedia)
        await self.db.commit()
        await self.db.refresh(nuevo_multimedia)
        return nuevo_multimedia
    
    async def obtener_multimedia_por_retorno(self, retorno_id: int) -> list[Multimedia]:
        query = select(Multimedia).where(Multimedia.retorno == retorno_id)
        resultado = await self.db.execute(query)
        return resultado.scalars().all()