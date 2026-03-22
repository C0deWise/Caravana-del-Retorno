from typing import Optional
from datetime import datetime, timedelta
from app.colonias.excepciones.excepciones import SolicitudEstadoInvalido, SolicitudNoEncontrada
from sqlalchemy.orm import Session

from app.colonias.models.solicitud_colonia import SolicitudColonia, EstadoSolicitud
from app.colonias.schemas.colonia_solicitud_schemas import SolicitudColoniaCrear


class SolicitudColoniaRepository:

    def crear_solicitud_colonia(self, db: Session, data: SolicitudColoniaCrear) -> SolicitudColonia:
        solicitud = SolicitudColonia(
            usuario_id=data.usuario_id,
            colonia_id=data.colonia_id,
            estado=EstadoSolicitud.pendiente,
        )
        db.add(solicitud)
        db.commit()
        db.refresh(solicitud)
        return solicitud

    def obtener_solicitud_por_id(self, db: Session, codigo: int) -> Optional[SolicitudColonia]:
        return db.query(SolicitudColonia).filter(
            SolicitudColonia.codigo == codigo
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
                SolicitudColonia.estado == EstadoSolicitud.pendiente,
                SolicitudColonia.fecha_creacion <= limite,
            )
            .update({"estado": EstadoSolicitud.expirada}, synchronize_session="fetch")
        )
        db.commit()
        return actualizadas
    
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