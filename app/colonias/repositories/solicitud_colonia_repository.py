from typing import Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session, joinedload
from app.colonias.models.solicitud_colonia import SolicitudColonia, EstadoSolicitud
from app.colonias.schemas.colonia_solicitud_schemas import SolicitudColoniaCrear


class SolicitudColoniaRepository:

    def crear_solicitud_colonia(self, db: Session, data: SolicitudColoniaCrear) -> SolicitudColonia:
        solicitud = SolicitudColonia(
            us_codigo=data.codigo_usuario,
            co_codigo=data.codigo_colonia,
            so_estado=EstadoSolicitud.pendiente,
        )
        db.add(solicitud)
        db.commit()
        db.refresh(solicitud)
        return solicitud


    def obtener_solicitudes_pendientes_por_colonia(self, db: Session, cod_colonia: int) -> list[SolicitudColonia]:
        return db.query(SolicitudColonia).filter(
            SolicitudColonia.co_codigo == cod_colonia,
            SolicitudColonia.so_estado == EstadoSolicitud.pendiente
        ).options(joinedload(SolicitudColonia.usuario)).all()
    
    def obtener_solicitudes_recientes_por_colonia(self, db: Session, cod_colonia: int) -> list[SolicitudColonia]:
        limite = datetime.utcnow() - timedelta(days=30)
        return db.query(SolicitudColonia).filter(
            SolicitudColonia.co_codigo == cod_colonia,
            SolicitudColonia.so_fecha_creacion > limite
        ).options(joinedload(SolicitudColonia.usuario)).all()
    
    def obtener_solicitudes_recientes_por_usuario(self, db: Session, cod_usuario: int) -> list[SolicitudColonia]:
        limite = datetime.utcnow() - timedelta(days=30)
        return db.query(SolicitudColonia).filter(
            SolicitudColonia.us_codigo == cod_usuario,
            SolicitudColonia.so_fecha_creacion > limite
        ).options(joinedload(SolicitudColonia.usuario)).all()


    def expirar_pendientes(self, db: Session) -> int:
        """Marca como 'expirada' toda solicitud pendiente con más de 30 días.
        Retorna la cantidad de registros actualizados."""
        limite = datetime.utcnow() - timedelta(days=30)
        actualizadas = (
            db.query(SolicitudColonia)
            .filter(
                SolicitudColonia.so_estado == EstadoSolicitud.pendiente,
                SolicitudColonia.so_fecha_creacion <= limite,
            )
            .update({"so_estado": EstadoSolicitud.expirada}, synchronize_session="fetch")
        )
        db.commit()
        return actualizadas
    

