from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.colonias.excepciones.excepciones import SolicitudEstadoInvalido, SolicitudNoEncontrada
from app.colonias.models.solicitud_colonia import SolicitudColonia
from app.colonias.repositories.solicitud_colonia_repository import SolicitudColoniaRepository 
from app.colonias.schemas.colonia_solicitud_schemas import MiembroRegistradoColoniaRespuesta, SolicitudColoniaCrear, SolicitudColoniaRespuesta
from app.notificaciones.events.events import EventoBase, TipoEvento
from app.notificaciones.events.patron_observer import Publicador
from app.notificaciones.services.notificacion_crear_service import NotificacionCrearService

class SolicitudColoniaService:

    def __init__(self, repositorio: SolicitudColoniaRepository, servicio_notificaciones: NotificacionCrearService):
        self.repositorio = repositorio
        self.publicador = Publicador(servicio_notificaciones)

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

    def _mapear_miembro_registrado(self, usuario) -> MiembroRegistradoColoniaRespuesta:
        return MiembroRegistradoColoniaRespuesta(
            codigo_usuario=usuario.us_codigo,
            nombre_usuario=usuario.us_nombre,
            apellido_usuario=usuario.us_apellido,
            codigo_colonia=usuario.co_codigo
        )

    async def crear_solicitud(self, data: SolicitudColoniaCrear) -> SolicitudColoniaRespuesta:
        if await self.repositorio.obtener_colonia_tiene_lider(data.codigo_colonia):
            
            solicitud = await self.repositorio.crear_solicitud_colonia(data)
            
            return self._mapear_solicitud(solicitud)
        else:
           usuario =  await self.repositorio.actualizar_colonia_usuario(data.codigo_usuario, data.codigo_colonia)
           return self._mapear_miembro_registrado(usuario)
        

    async def _rechazar_solicitudes_colonia_pendientes_por_usuario(self, cod_usuario: int) -> int:
        return await self.repositorio.rechazar_solicitudes_pendientes_por_usuario(cod_usuario)

    async def obtener_solicitudes_pendientes_colonia(self, cod_colonia: int) -> list[SolicitudColoniaRespuesta]:
        solicitudes = await self.repositorio.obtener_solicitudes_pendientes_por_colonia(cod_colonia)
        return [self._mapear_solicitud(s) for s in solicitudes]

    async def obtener_solicitudes_recientes_colonia(self, cod_colonia: int) -> list[SolicitudColoniaRespuesta]:
        solicitudes = await self.repositorio.obtener_solicitudes_recientes_por_colonia(cod_colonia)
        return [self._mapear_solicitud(s) for s in solicitudes]

    async def obtener_solicitudes_recientes_usuario(self, cod_usuario: int) -> list[SolicitudColoniaRespuesta]:
        solicitudes = await self.repositorio.obtener_solicitudes_recientes_por_usuario(cod_usuario)
        return [self._mapear_solicitud(s) for s in solicitudes]

    async def expirar_solicitudes_vencidas(self) -> int:
        return await self.repositorio.expirar_pendientes()
    
    async def aceptar_solicitud (self, codigo: int) -> SolicitudColoniaRespuesta:
        """Acepta una solicitud pendiente, cambiando su estado a 'aceptada'."""
        try:
            solicitud = await self.repositorio.aceptar_solicitud_colonia(codigo)
            await self._rechazar_solicitudes_colonia_pendientes_por_usuario(solicitud.us_codigo)
            evento = EventoBase(
                tipo_evento=TipoEvento.SOLICITUD_COLONIA_ACEPTADA,
                datos={"colonia_ciudad": solicitud.colonia.ciudad},
                receptores=[solicitud.us_codigo]) 
            await self.publicador.notificar(
                evento=evento
            )
            return self._mapear_solicitud(solicitud)
        except SolicitudNoEncontrada as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        except SolicitudEstadoInvalido as e:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
        
    
    async def rechazar_solicitud (self, codigo: int) -> SolicitudColoniaRespuesta:
        """Rechaza una solicitud pendiente, cambiando su estado a 'rechazada'."""
        try:
            solicitud = await self.repositorio.rechazar_solicitud_colonia(codigo)
            evento = EventoBase(
                tipo_evento=TipoEvento.SOLICITUD_COLONIA_RECHAZADA,
                datos={"colonia_ciudad": solicitud.colonia.ciudad},
                receptores=[solicitud.us_codigo]) 
            await self.publicador.notificar(
                evento=evento
            )
            return self._mapear_solicitud(solicitud)
        except SolicitudNoEncontrada as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        except SolicitudEstadoInvalido as e:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    
    async def obtener_solicitud(self,codigo: int) -> SolicitudColoniaRespuesta:
        solicitud = await self.repositorio.obtener_solicitud_por_id(codigo)
        if not solicitud:
            raise ValueError(f"Solicitud con código {codigo} no encontrada.")
        return self._mapear_solicitud(solicitud)