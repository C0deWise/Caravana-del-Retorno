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
      
     def obtener_solicitud_por_id(self, db: Session, codigo: int) -> Optional[SolicitudColonia]:
        return db.query(SolicitudColonia).filter(
            SolicitudColonia.codigo == codigo
        ).first()

    def get_all(self, db: Session) -> list[SolicitudColonia]:
        return db.query(SolicitudColonia).all()
      
     def aceptar_solicitud_colonia(self, db: Session, codigo: int) -> SolicitudColonia:
        """Cambia el estado de una solicitud a aceptada"""
        solicitud = self.obtener_solicitud_por_id(db, codigo)

        if not solicitud:
            raise SolicitudNoEncontrada(f"Solicitud con código {codigo} no encontrada.")
        
        if solicitud.estado != EstadoSolicitud.pendiente:
            raise SolicitudEstadoInvalido(f"Solo se pueden aceptar solicitudes pendientes. Solicitud {codigo} está en estado {solicitud.estado.value}.")
        
        solicitud.estado = EstadoSolicitud.aceptada
        db.commit()
        db.refresh(solicitud)

        return solicitud

    def rechazar_solicitud_colonia(self, db: Session, codigo: int) -> SolicitudColonia:
        """Cambia el estado de una solicitud a rechazada"""
        solicitud = self.obtener_solicitud_por_id(db, codigo)

        if not solicitud:
            raise SolicitudNoEncontrada(f"Solicitud con código {codigo} no encontrada.")
        
        if solicitud.estado != EstadoSolicitud.pendiente:
            raise SolicitudEstadoInvalido(f"Solo se pueden rechazar solicitudes pendientes. Solicitud {codigo} está en estado {solicitud.estado.value}.")
        
        solicitud.estado = EstadoSolicitud.rechazada
        db.commit()
        db.refresh(solicitud)

        return solicitud
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
