"""
Modulo de repositorio para la gestión de multimedia en la aplicación. Contiene la clase MultimediaRepositorio,
que proporciona métodos para crear nuevos registros de multimedia y obtener multimedia asociado a una publicación
específica.
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.multimedia.modelos.multimedia_modelo import Multimedia
from app.multimedia.esquemas.multimedia_esquemas import MultimediaCrear

class MultimediaRepositorio:
    def __init__(self, db:AsyncSession):
        self.db = db

    async def crear_multimedia(self, data:MultimediaCrear) -> Multimedia:
        """Crea un nuevo registro de multimedia en la base de datos."""
        nuevo_multimedia = Multimedia(
            publicacion=data.publicacion,
            tipo=data.tipo,
            formato=data.formato,
            url=data.url,
            descripcion=data.descripcion
        )
        self.db.add(nuevo_multimedia)
        print(f"Multimedia agregado a la sesión: {nuevo_multimedia}")
        await self.db.commit()
        await self.db.refresh(nuevo_multimedia)
        return nuevo_multimedia
    
    async def obtener_multimedia_por_publicacion(self, publicacion_id: int) -> list[Multimedia]:
        """Obtiene la lista de archivos multimedia asociados a una publicación específica."""
        query = select(Multimedia).where(Multimedia.publicacion == publicacion_id)
        resultado = await self.db.execute(query)
        return resultado.scalars().all()