from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.colonias.excepciones.excepciones import SolicitudEstadoInvalido, SolicitudNoEncontrada
from app.colonias.models.solicitud_colonia import SolicitudColonia
from app.colonias.repositories.solicitud_colonia_repository import SolicitudColoniaRepository 
from app.colonias.schemas.colonia_solicitud_schemas import SolicitudColoniaCrear


class SolicitudColoniaService:

    def crear_solicitud(self, db: Session, data: SolicitudColoniaCrear) -> SolicitudColonia:
        return SolicitudColoniaRepository().crear_solicitud_colonia(db, data)

    def obtener_solicitud(self, db: Session, codigo: int) -> SolicitudColonia:
        solicitud = SolicitudColoniaRepository().obtener_solicitud_por_id(db, codigo)
        if not solicitud:
            raise ValueError(f"Solicitud con código {codigo} no encontrada.")
        return solicitud

    def expirar_solicitudes_vencidas(self, db: Session) -> int:
        """Expira todas las solicitudes pendientes con más de 30 días.
        Retorna la cantidad de registros afectados."""
        return SolicitudColoniaRepository().expirar_pendientes(db)
    
    def aceptar_solicitud (self, db: Session, codigo: int) -> SolicitudColonia:
        """Acepta una solicitud pendiente, cambiando su estado a 'aceptada'."""
        try:
            return SolicitudColoniaRepository().aceptar_solicitud_colonia(db, codigo)
        except SolicitudNoEncontrada as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        except SolicitudEstadoInvalido as e:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
        
    
    def rechazar_solicitud (self, db: Session, codigo: int) -> SolicitudColonia:
        """Rechaza una solicitud pendiente, cambiando su estado a 'rechazada'."""
        try:
            return SolicitudColoniaRepository().rechazar_solicitud_colonia(db, codigo)
        except SolicitudNoEncontrada as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        except SolicitudEstadoInvalido as e:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
        