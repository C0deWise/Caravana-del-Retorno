




from app.notificaciones.repositories.notificacion_repositorio import NotificacionRepository
from app.notificaciones.schemas.notificacion_esquema import NotificacionRespuesta, Evento
from app.usuarios.repository.usuario_repositorio import UsuarioRepositorio


class NotificacionConsultarActualizarService:
    def __init__(self, notificacion_repository: NotificacionRepository, usuario_repository: UsuarioRepositorio):
        self.notificacion_repository = notificacion_repository
        self.usuario_repository = usuario_repository

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

    async def consultar_notificaciones_no_leidas_usuario(self, id_usuario: int) -> list[NotificacionRespuesta]:
        """Consulta las notificaciones no leídas de un usuario específico."""
        usuario = await self.usuario_repository.obtener_usuario_por_id(id_usuario)
        if not usuario:
            raise ValueError(f"No se encontró el usuario con ID {id_usuario}")
        notificaciones = await self.notificacion_repository.obtener_notificaciones_no_leidas_usuario(id_usuario)
        return [self._mapear_notificacion(notif) for notif in notificaciones]

    async def actualizar_estado_notificacion_leida_por_id(self, id_notificacion: int) -> NotificacionRespuesta:
        """Actualiza el estado de una notificación específica a leída."""
        notificacion = await self.notificacion_repository.obtener_notificacion_id(id_notificacion)
        if not notificacion:
            raise ValueError(f"No se encontró la notificación con ID {id_notificacion}")
        notificacion_actualizada = await self.notificacion_repository.actualizar_estado_notificacion_leida(id_notificacion)
        return self._mapear_notificacion(notificacion_actualizada)
    
    async def actualizar_estado_notificacion_leida_lote(self, notificaciones_id: list[int]) -> list[NotificacionRespuesta]:
        """Actualiza el estado de múltiples notificaciones a leídas."""
        notificaciones = await self.notificacion_repository.obtener_notificaciones_id_lote(notificaciones_id)
        
        if len(notificaciones) != len(notificaciones_id):
            # Identificar cuáles IDs no fueron encontrados
            ids_encontrados = {notif.no_codigo for notif in notificaciones}
            ids_no_encontrados = [id_notif for id_notif in notificaciones_id if id_notif not in ids_encontrados]
            raise ValueError(f"Notificaciones no encontradas para los IDs: {ids_no_encontrados}")
        
        await self.notificacion_repository.actualizar_estado_notificacion_leida_lote(notificaciones_id)
        notificaciones_actualizadas = await self.notificacion_repository.obtener_notificaciones_id_lote(notificaciones_id)
        return [self._mapear_notificacion(notif) for notif in notificaciones_actualizadas]
        
    
    async def actualizar_estado_notificacion_leida_lote_por_usuario(self, id_usuario: int) -> list[NotificacionRespuesta]:
        """Actualiza el estado de todas las notificaciones de un usuario a leídas."""
        usuario = await self.usuario_repository.obtener_usuario_por_id(id_usuario)
        if not usuario:
            raise ValueError(f"No se encontró el usuario con ID {id_usuario}")
        
        notificaciones_actualizadas = await self.notificacion_repository.actualizar_estado_notificacion_leida_lote_por_usuario(id_usuario)
        
        return [self._mapear_notificacion(notif) for notif in notificaciones_actualizadas]
           
    
    async def consultar_notificacion_id(self, id_notificacion: int) -> NotificacionRespuesta:
        """Consulta una notificación específica por su ID."""
        notificacion = await self.notificacion_repository.obtener_notificacion_id(id_notificacion)
        if not notificacion:
            raise ValueError(f"No se encontró la notificación con ID {id_notificacion}")
        return self._mapear_notificacion(notificacion)