from fastapi import Depends
from sqlalchemy.orm import Session

from app.colonias.models.solicitud_colonia import SolicitudColonia
from app.colonias.repositories.solicitud_colonia_repository import SolicitudColoniaRepository 
from app.colonias.schemas.colonia_solicitud_schemas import SolicitudColoniaCrear, SolicitudColoniaRespuesta



class SolicitudColoniaService:

    def _mapear_solicitud(self, solicitud: SolicitudColonia) -> SolicitudColoniaRespuesta:
        return SolicitudColoniaRespuesta(
            codigo=solicitud.so_codigo,
            estado=solicitud.so_estado,
            fecha_creacion=solicitud.so_fecha_creacion,
            codigo_usuario=solicitud.us_codigo,
            codigo_colonia=solicitud.co_codigo,
            nombre_usuario=solicitud.usuario.us_nombre,
            apellido_usuario=solicitud.usuario.us_apellido,
        )

    def crear_solicitud(self, db: Session, data: SolicitudColoniaCrear) -> SolicitudColoniaRespuesta:
        solicitud = SolicitudColoniaRepository().crear_solicitud_colonia(db, data)
        return self._mapear_solicitud(solicitud)

    def obtener_solicitudes_pendientes_colonia(self, db: Session, cod_colonia: int) -> list[SolicitudColoniaRespuesta]:
        solicitudes = SolicitudColoniaRepository().obtener_solicitudes_pendientes_por_colonia(db, cod_colonia)
        return [self._mapear_solicitud(s) for s in solicitudes]

    def obtener_solicitudes_recientes_colonia(self, db: Session, cod_colonia: int) -> list[SolicitudColoniaRespuesta]:
        solicitudes = SolicitudColoniaRepository().obtener_solicitudes_recientes_por_colonia(db, cod_colonia)
        return [self._mapear_solicitud(s) for s in solicitudes]

    def obtener_solicitudes_recientes_usuario(self, db: Session, cod_usuario: int) -> list[SolicitudColoniaRespuesta]:
        solicitudes = SolicitudColoniaRepository().obtener_solicitudes_recientes_por_usuario(db, cod_usuario)
        return [self._mapear_solicitud(s) for s in solicitudes]

    def expirar_solicitudes_vencidas(self, db: Session) -> int:
        """Expira todas las solicitudes pendientes con más de 30 días.
        Retorna la cantidad de registros afectados."""
        return SolicitudColoniaRepository().expirar_pendientes(db)

