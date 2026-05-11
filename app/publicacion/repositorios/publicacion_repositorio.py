from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import joinedload, selectinload

from app.multimedia.modelos.multimedia_modelo import Multimedia
from app.publicacion.modelos.publicacion_modelo import Publicacion
from app.publicacion.esquemas.publicacion_esquema import PublicacionCrear

class PublicacionRepositorio:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def crear_publicacion(self, datos: PublicacionCrear) -> Publicacion:
        nueva_publicacion = Publicacion(
            retorno=datos.retorno,
            autor=datos.autor,
            resena=datos.resena,
            titulo=datos.titulo
        )
        self.db.add(nueva_publicacion)
        await self.db.commit()
        await self.db.refresh(nueva_publicacion)
        return nueva_publicacion
    
    async def consultar_publicacion_por_codigo(self, codigo: int) -> Publicacion:
        query = (
            select(Publicacion)
            .where(Publicacion.codigo == codigo)
            .options(selectinload(Publicacion.multimedia_lista))
        )
        resultado = await self.db.execute(query)
        return resultado.scalars().first()
    
    async def consultar_publicaciones_por_retorno(self, retorno_id: int) -> list[Publicacion]:
        query = (
            select(Publicacion)
            .where(Publicacion.retorno == retorno_id)
            .options(selectinload(Publicacion.multimedia_lista))
            .order_by(Publicacion.codigo)
        )
        resultado = await self.db.execute(query)
        return resultado.unique().scalars().all()
