from datetime import datetime, timedelta
from sqlalchemy.orm import joinedload
from app.colonias.models.solicitud_colonia import SolicitudColonia, EstadoSolicitud
from app.colonias.schemas.colonia_solicitud_schemas import SolicitudColoniaCrear
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

class SolicitudColoniaRepository:
 
    def __init__(self, db: AsyncSession):
        self.db = db
 
    async def crear_solicitud_colonia(self, data: SolicitudColoniaCrear) -> SolicitudColonia:
        solicitud = SolicitudColonia(
            us_codigo=data.codigo_usuario,
            co_codigo=data.codigo_colonia,
            so_estado=EstadoSolicitud.pendiente,
        )
        self.db.add(solicitud)
        await self.db.commit()
        await self.db.refresh(solicitud, attribute_names=["usuario"])
        return solicitud
 
    async def obtener_solicitudes_pendientes_por_colonia(self, cod_colonia: int) -> list[SolicitudColonia]:
        resultado = await self.db.execute(
            select(SolicitudColonia)
            .where(
                SolicitudColonia.co_codigo == cod_colonia,
                SolicitudColonia.so_estado == EstadoSolicitud.pendiente,
            )
            .options(joinedload(SolicitudColonia.usuario))
        )
        return resultado.scalars().all()
 
    async def obtener_solicitudes_recientes_por_colonia(self, cod_colonia: int) -> list[SolicitudColonia]:
        limite = datetime.utcnow() - timedelta(days=30)
        resultado = await self.db.execute(
            select(SolicitudColonia)
            .where(
                SolicitudColonia.co_codigo == cod_colonia,
                SolicitudColonia.so_fecha_creacion > limite,
            )
            .options(joinedload(SolicitudColonia.usuario))
        )
        return resultado.scalars().all()
 
    async def obtener_solicitudes_recientes_por_usuario(self, cod_usuario: int) -> list[SolicitudColonia]:
        limite = datetime.utcnow() - timedelta(days=30)
        resultado = await self.db.execute(
            select(SolicitudColonia)
            .where(
                SolicitudColonia.us_codigo == cod_usuario,
                SolicitudColonia.so_fecha_creacion > limite,
            )
            .options(joinedload(SolicitudColonia.usuario))
        )
        return resultado.scalars().all()
 
    async def expirar_pendientes(self) -> int:
        limite = datetime.utcnow() - timedelta(days=30)
        resultado = await self.db.execute(
            update(SolicitudColonia)
            .where(
                SolicitudColonia.so_estado == EstadoSolicitud.pendiente,
                SolicitudColonia.so_fecha_creacion <= limite,
            )
            .values(so_estado=EstadoSolicitud.expirada)
            .execution_options(synchronize_session="fetch")
        )
        await self.db.commit()
        return resultado.rowcount