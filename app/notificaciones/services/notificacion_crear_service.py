


from app.notificaciones.repositories.notificacion_repositorio import NotificacionRepository
from app.notificaciones.schemas.notificacion_esquema import Evento, NotificacionCrear, NotificacionCrearLote, NotificacionRespuesta

class NotificacionCrearService:
    def __init__(self, repositorio_notificacion: NotificacionRepository):
        self.repositorio_notificacion = repositorio_notificacion
    
    def _mapear_notificacion(self, notificacion) -> NotificacionRespuesta:
        """Convierte una Notificacion a NotificacionRespuesta."""
        evento_obj = Evento(
            codigo=notificacion.evento.ev_codigo,
            nombre=notificacion.evento.ev_nombre,
            descripcion=notificacion.evento.ev_descripcion
        )
        return NotificacionRespuesta(
            codigo=notificacion.no_codigo,
            mensaje=notificacion.no_mensaje,
            codigo_receptor=notificacion.us_codigo_receptor,
            evento=evento_obj,
            time_stamp=notificacion.no_time_stamp.isoformat(),
            estado=notificacion.no_estado.value
        )

    async def crear_notificacion(self, notificacion: NotificacionCrear) -> NotificacionRespuesta:
        notificacion_creada = await self.repositorio_notificacion.crear_notificacion(notificacion)
        return self._mapear_notificacion(notificacion_creada)
    
    async def crear_notificacion_lote(self, notificaciones: NotificacionCrearLote) -> list[NotificacionRespuesta]:
        notificaciones_creadas = await self.repositorio_notificacion.crear_notificacion_lote(notificaciones)
        notificaciones_respuesta = []
        for notificacion in notificaciones_creadas:
            notificaciones_respuesta.append(self._mapear_notificacion(notificacion))
        return notificaciones_respuesta