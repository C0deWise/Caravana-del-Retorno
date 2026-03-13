from typing import Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.colonias.models.solicitud_colonia import SolicitudColonia, EstadoSolicitud
from app.colonias.schemas.colonia_solicitud_schemas import SolicitudColoniaCrear


class SolicitudColoniaRepository:

    def crear_solicitud_colonia(self, db: Session, data: SolicitudColoniaCrear) -> SolicitudColonia:
        solicitud = SolicitudColonia(
            us_codigo=data.us_codigo,
            co_codigo=data.co_codigo,
            so_estado=EstadoSolicitud.pendiente,
        )
        db.add(solicitud)
        db.commit()
        db.refresh(solicitud)
        return solicitud

    def obtener_solicitud_por_id(self, db: Session, so_codigo: int) -> Optional[SolicitudColonia]:
        return db.query(SolicitudColonia).filter(
            SolicitudColonia.so_codigo == so_codigo
        ).first()

    def get_all(self, db: Session) -> list[SolicitudColonia]:
        return db.query(SolicitudColonia).all()

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
    

