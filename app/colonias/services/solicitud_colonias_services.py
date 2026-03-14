from sqlalchemy.orm import Session

from app.colonias.models.solicitud_colonia import SolicitudColonia
from app.colonias.repositories.solicitud_colonia_repository import SolicitudColoniaRepository 
from app.colonias.schemas.colonia_solicitud_schemas import SolicitudColoniaCrear, SolicitudColoniaRespuesta
from app.usuarios.services.usuario_servicio import UsuarioService

class SolicitudColoniaService:

    def crear_solicitud(self, db: Session, data: SolicitudColoniaCrear) -> SolicitudColonia:
        if not UsuarioService().existe_usuario(db, data.codigo_usuario):
            raise ValueError(f"El usuario con código {data.codigo_usuario} no existe.")
        return SolicitudColoniaRepository().crear_solicitud_colonia(db, data)

    
    def obtener_solicitudes_pendientes_colonia(self, db: Session, cod_colonia: int) -> list[SolicitudColoniaRespuesta]:
        return SolicitudColoniaRepository().obtener_solicitudes_pendientes_por_colonia (db, cod_colonia)

    def obtener_solicitudes_recientes_colonia(self, db: Session, cod_colonia: int) -> list[SolicitudColoniaRespuesta]:
        return SolicitudColoniaRepository().obtener_solicitudes_recientes_por_colonia(db, cod_colonia)
    
    def obtener_solicitudes_recientes_usuario(self, db: Session, cod_usuario: int) -> list[SolicitudColoniaRespuesta]:
        return SolicitudColoniaRepository().obtener_solicitudes_recientes_por_usuario(db, cod_usuario)

    def expirar_solicitudes_vencidas(self, db: Session) -> int:
        """Expira todas las solicitudes pendientes con más de 30 días.
        Retorna la cantidad de registros afectados."""
        return SolicitudColoniaRepository().expirar_pendientes(db)

