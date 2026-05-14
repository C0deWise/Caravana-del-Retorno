"""
Repositorio de acceso a datos para Retorno.
Encapsula operaciones de persistencia como creación y consulta,
sin incluir lógica de negocio.
"""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.retornos.modelos.retorno_modelo import Retorno
from app.retornos.esquemas.retorno_esquemas import RetornoCreate, RetornoEstado
import datetime


class RetornoRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, data: RetornoCreate) -> Retorno:
        """Crea y persiste un nuevo registro de retorno en la base de datos."""
        retorno = Retorno(
            fecha_creacion=datetime.datetime.now(),
            anio=data.anio,
            estado=data.estado,
        )
        self.db.add(retorno)
        await self.db.commit()
        await self.db.refresh(retorno)
        return retorno

    async def get_all(self) -> list[Retorno]:
        """Obtiene todos los registros de retorno."""
        result = await self.db.execute(select(Retorno))
        return list(result.scalars().all())

    async def get_by_codigo(self, codigo: int) -> Retorno | None:
        """Obtiene un retorno por su código primario."""
        result = await self.db.execute(select(Retorno).filter(Retorno.codigo == codigo))
        return result.scalars().first()
    
    async def get_by_fecha(self, fecha: datetime.date) -> Retorno | None:
        """Busca un retorno existente por fecha de creación."""
        result = await self.db.execute(select(Retorno).filter(Retorno.fecha_creacion == fecha))
        return result.scalars().first()

    async def get_by_anio(self, anio: int) -> Retorno | None:
        """Busca un retorno existente por año."""
        result = await self.db.execute(select(Retorno).filter(Retorno.anio == anio))
        return result.scalars().first()
    
    async def cambiar_estado_retorno(self, codigo: int, nuevo_estado: RetornoEstado) -> Retorno | None:
        """Actualiza el estado de un retorno existente."""
        retorno = await self.get_by_codigo(codigo)
        if retorno:
            retorno.estado = nuevo_estado.value
            self.db.add(retorno)
            await self.db.commit()
            await self.db.refresh(retorno)
            return retorno
        return None

    async def obtener_ultimo_retorno(self) -> Retorno | None:
        """Obtiene el retorno más reciente basado en el año."""
        result = await self.db.execute(select(Retorno).order_by(Retorno.anio.desc()).limit(1))
        return result.scalars().first()
    
    async def obtener_retorno_por_estado(self, estado: RetornoEstado) -> list[Retorno]:
        """Obtiene todos los retornos que coincidan con un estado específico."""
        result = await self.db.execute(select(Retorno).filter(Retorno.estado == estado.value))
        return list(result.scalars().all())
