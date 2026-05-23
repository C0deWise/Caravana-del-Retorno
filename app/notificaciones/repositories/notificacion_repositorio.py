

from sqlalchemy import select, update
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.notificaciones.models.notificacion_model import Notificacion, NotificacionEstado

from app.notificaciones.schemas.notificacion_esquema import NotificacionCrear, NotificacionCrearLote

class NotificacionRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def crear_notificacion(self, notificacion:NotificacionCrear) -> Notificacion:
        notificacion = Notificacion(
            no_mensaje=notificacion.no_mensaje,
            us_codigo_receptor=notificacion.us_codigo_receptor,
            ev_codigo=notificacion.ev_codigo
        )
        self.db.add(notificacion)
        await self.db.commit()
        await self.db.refresh(notificacion)
        # Cargar la relación evento después del refresh
        await self.db.refresh(notificacion, attribute_names=['evento'])
        return notificacion
    
    async def crear_notificacion_lote(self, notificaciones: NotificacionCrearLote) -> list[Notificacion]:
        notificaciones_creadas = []
        for codigo_receptor in notificaciones.codigo_receptores:
            notificacion = Notificacion(
                no_mensaje=notificaciones.no_mensaje,
                us_codigo_receptor=codigo_receptor,
                ev_codigo=notificaciones.codigo_evento
            )
            self.db.add(notificacion)
            notificaciones_creadas.append(notificacion)
        await self.db.commit()
        for notificacion in notificaciones_creadas:
            await self.db.refresh(notificacion)
            # Cargar la relación evento después del refresh
            await self.db.refresh(notificacion, attribute_names=['evento'])
        return notificaciones_creadas
    
    async def obtener_notificacion_id(self, notificacion_id:int) -> Notificacion | None:
        sentencia = select(Notificacion).options(selectinload(Notificacion.evento)).filter(Notificacion.no_codigo == notificacion_id)
        resultado = await self.db.execute(sentencia)
        return resultado.scalars().first()
    
    async def obtener_notificaciones_id_lote(self, notificaciones_id: list[int]) -> list[Notificacion]:
        sentencia = select(Notificacion).options(selectinload(Notificacion.evento)).filter(Notificacion.no_codigo.in_(notificaciones_id))
        resultado = await self.db.execute(sentencia)
        return resultado.scalars().all()
    
    async def actualizar_estado_notificacion_leida(self, notificacion_id: int) -> Notificacion:
        notificacion = await self.obtener_notificacion_id(notificacion_id)
        notificacion.no_estado = NotificacionEstado.LEIDA
        await self.db.commit()
        await self.db.refresh(notificacion)
        return notificacion

    async def actualizar_estado_notificacion_leida_lote(self, notificaciones_id: list[int]) -> list[Notificacion]:
        sentencia = update(Notificacion).where(
            Notificacion.no_codigo.in_(notificaciones_id)
        ).values(no_estado=NotificacionEstado.LEIDA)
        await self.db.execute(sentencia)
        await self.db.commit()
        notificaciones_actualizadas = await self.obtener_notificaciones_id_lote(notificaciones_id)
        return notificaciones_actualizadas

    async def actualizar_estado_notificacion_leida_lote_por_usuario(self, usuario_id: int) -> list[Notificacion]:
        notificaciones_no_leidas = await self.obtener_notificaciones_no_leidas_usuario(usuario_id)
        notificaciones_id = [notif.no_codigo for notif in notificaciones_no_leidas]
        sentencia = update(Notificacion).where(
            Notificacion.us_codigo_receptor == usuario_id
        ).values(no_estado=NotificacionEstado.LEIDA)
        await self.db.execute(sentencia)
        await self.db.commit()
        notificaciones_actualizadas = await self.obtener_notificaciones_id_lote(notificaciones_id)
        return notificaciones_actualizadas
    
    async def obtener_notificaciones_no_leidas_usuario(self, usuario_id: int) -> list[Notificacion]:
        sentencia = select(Notificacion).options(selectinload(Notificacion.evento)).where(
            (Notificacion.us_codigo_receptor == usuario_id) &
            (Notificacion.no_estado == NotificacionEstado.SIN_LEER)
        )
        resultado = await self.db.execute(sentencia)
        return resultado.scalars().all()

