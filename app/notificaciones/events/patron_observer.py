



from abc import ABC
from typing import Annotated

from fastapi import Depends

from app.notificaciones.events.events import (
    EventoBase, 
    TipoEvento,
    EventoSolicitudColoniaAceptada,
    EventoSolicitudColoniaRechazada,
    EventoDesactivarColonia,
    EventoEstablecerLiderColonia,
    EventoEliminarLiderColonia,
    EventoRegistroGrupoRetorno,
    EventoActualizacionRegistroGrupo,
    EventoDarseBajaGrupo,
    EventoEliminarGrupoRetorno,
    EventoDarseBajaRetorno
)
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.notificaciones.schemas.notificacion_esquema import NotificacionCrear, NotificacionCrearLote
from app.notificaciones.services.notificacion_crear_service import NotificacionCrearService
from app.notificaciones.repositories.notificacion_repositorio import NotificacionRepository






class FabricaEventos:
    """Fábrica para crear objetos de eventos basado en TipoEvento."""
    
    # Mapeo de tipos de eventos a sus clases correspondientes
    _MAPA_EVENTOS = {
        TipoEvento.SOLICITUD_COLONIA_ACEPTADA: EventoSolicitudColoniaAceptada,
        TipoEvento.SOLICITUD_COLONIA_RECHAZADA: EventoSolicitudColoniaRechazada,
        TipoEvento.DESACTIVAR_COLONIA: EventoDesactivarColonia,
        TipoEvento.ESTABLER_LIDER_COLONIA: EventoEstablecerLiderColonia,
        TipoEvento.ELIMINAR_LIDER_COLONIA: EventoEliminarLiderColonia,
        TipoEvento.REGISTRO_GRUPO_RETORNO: EventoRegistroGrupoRetorno,
        TipoEvento.ACTUALIZACION_REGISTRO_GRUPO: EventoActualizacionRegistroGrupo,
        TipoEvento.DARSE_BAJA_GRUPO: EventoDarseBajaGrupo,
        TipoEvento.ELIMINAR_GRUPO_RETORNO: EventoEliminarGrupoRetorno,
        TipoEvento.DARSE_BAJA_RETORNO: EventoDarseBajaRetorno,
    }
    
    @classmethod
    def crear_evento(cls, tipo_evento: TipoEvento, datos, receptores: list) -> EventoBase:
        """
        Crea una instancia de evento basado en el tipo especificado.
        
        Args:
            tipo_evento: El tipo de evento (TipoEvento)
            datos: Diccionario con datos específicos del evento
            receptores: Lista de IDs de usuarios receptores
            
        Returns:
            Una instancia de la clase de evento correspondiente
            
        Raises:
            ValueError: Si el tipo de evento no es reconocido
        """
        clase_evento = cls._MAPA_EVENTOS.get(tipo_evento)
        
        if clase_evento is None:
            raise ValueError(f"Tipo de evento no reconocido: {tipo_evento}")
        
        return clase_evento(datos, receptores)

class Publicador:
    """Servicio publicador de notificaciones usando el patrón Observer."""
    
    def __init__(self, servicio_notificaciones: NotificacionCrearService):
        self.servicio = servicio_notificaciones

    async def notificar(self, evento: EventoBase):
        """
        Notifica a múltiples receptores mediante la creación de notificaciones en lote.
        
        Args:
            evento: El evento que contiene los datos y receptores
        """
        # Crear el evento particular usando la fábrica
        evento_particular = FabricaEventos.crear_evento(evento.tipo_evento, evento.datos, evento.receptores)
        evento_particular.construir_mensaje()

        notificacion = NotificacionCrearLote(
            no_mensaje=evento_particular.mensaje,
            codigo_receptores=evento.receptores,
            codigo_evento=evento.codigo_evento
        )
        # Crear la notificación en lote
        await self.servicio.crear_notificacion_lote(notificacion)

        
