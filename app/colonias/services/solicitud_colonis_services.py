from sqlalchemy.orm import Session

from app.colonias.models.solicitud_colonia import SolicitudColonia
from app.colonias.repositories.solicitud_colonia_repository import SolicitudColoniaRepository 
from app.colonias.schemas.colonia_solicitud_schemas import SolicitudColoniaCrear


class SolicitudColoniaService:

    def crear_solicitud(self, db: Session, data: SolicitudColoniaCrear) -> SolicitudColonia:
        return SolicitudColoniaRepository().crear_solicitud_colonia(db, data)

    def obtener_solicitud(self, db: Session, so_codigo: int) -> SolicitudColonia:
        solicitud = SolicitudColoniaRepository().obtener_solicitud_por_id(db, so_codigo)
        if not solicitud:
            raise ValueError(f"Solicitud con código {so_codigo} no encontrada.")
        return solicitud

    def expirar_solicitudes_vencidas(self, db: Session) -> int:
        """Expira todas las solicitudes pendientes con más de 30 días.
        Retorna la cantidad de registros afectados."""
        return SolicitudColoniaRepository().expirar_pendientes(db)

