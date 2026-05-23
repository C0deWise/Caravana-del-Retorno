

from enum import Enum


class TipoEvento(Enum):
    """Enumeración para los tipos de eventos de notificaciones."""
    SOLICITUD_COLONIA_ACEPTADA = "solicitud_colonia_aceptada"
    SOLICITUD_COLONIA_RECHAZADA = "solicitud_colonia_rechazada"
    DESACTIVAR_COLONIA = "desactivar_colonia"
    ESTABLER_LIDER_COLONIA = "establecer_lider_colonia"
    ELIMINAR_LIDER_COLONIA = "eliminar_lider_colonia"

    REGISTRO_GRUPO_RETORNO = "registro_grupo_retorno"
    ACTUALIZACION_REGISTRO_GRUPO = "actualizacion_registro_grupo"
    DARSE_BAJA_GRUPO = "darse_baja_grupo"
    ELIMINAR_GRUPO_RETORNO = "eliminar_grupo_retorno"

    DARSE_BAJA_RETORNO = "darse_baja_retorno"


class MapeoEventosIds:
    """Mapeo estático entre tipos de eventos y sus IDs en la BD.
    
    Los IDs corresponden a los eventos creados por seed_eventos.py en orden.
    Este mapeo evita consultas a la BD innecesarias.
    """
    
    # Mapeo de TipoEvento -> (nombre_evento, id_evento)
    _MAPEO = {
        TipoEvento.DARSE_BAJA_GRUPO: 1,  # "Salida de grupo de retorno"
        TipoEvento.DARSE_BAJA_RETORNO: 2,  # "Salida de retorno"
        TipoEvento.ESTABLER_LIDER_COLONIA: 3,  # "Designación de líder"
        TipoEvento.ELIMINAR_LIDER_COLONIA: 4,  # "Revocación de líder"
        TipoEvento.SOLICITUD_COLONIA_ACEPTADA: 5,  # "Aceptación en colonia"
        TipoEvento.SOLICITUD_COLONIA_RECHAZADA: 6,  # "Rechazo en colonia"
        TipoEvento.ELIMINAR_GRUPO_RETORNO: 7,  # "Cancelación de grupo de retorno"
        TipoEvento.REGISTRO_GRUPO_RETORNO: 8,  # "Registro de grupo a retorno"
        TipoEvento.ACTUALIZACION_REGISTRO_GRUPO: 9,  # "Edición de registro de grupo"
        TipoEvento.DESACTIVAR_COLONIA: 10,  # "Desactivación de colonia"
    }
    
    @classmethod
    def obtener_id_evento(cls, tipo_evento: TipoEvento) -> int:
        """
        Obtiene el ID del evento en la BD basado en su tipo.
        
        Args:
            tipo_evento: El tipo de evento (TipoEvento)
            
        Returns:
            El ID del evento en la BD
            
        Raises:
            ValueError: Si el tipo de evento no está mapeado
        """
        id_evento = cls._MAPEO.get(tipo_evento)
        if id_evento is None:
            raise ValueError(f"Tipo de evento no mapeado: {tipo_evento}")
        return id_evento
    
    
   
class EventoBase:
    """Clase base para eventos de notificaciones."""
    
    def __init__(self, tipo_evento: TipoEvento, datos, receptores: list, mensaje: str = ""):
        self.tipo_evento = tipo_evento
        self.datos = datos
        self.receptores = receptores
        self.mensaje = mensaje
        # Obtener el ID del evento automáticamente
        self.codigo_evento = MapeoEventosIds.obtener_id_evento(tipo_evento)

    def construir_mensaje(self) -> str:
        """Construye el mensaje de notificación basado en los datos del evento."""
        return self.mensaje    

    def __repr__(self) -> str:
        return f"EventoBase(tipo_evento={self.tipo_evento!r}, datos={self.datos!r}, receptores={self.receptores!r}, mensaje={self.mensaje!r})"
    

class EventoSolicitudColoniaAceptada(EventoBase):
    def __init__(self, datos, receptores):
        super().__init__(TipoEvento.SOLICITUD_COLONIA_ACEPTADA, datos, receptores)

    def construir_mensaje(self) -> str:
        ciudad_colonia = self.datos.get("colonia_ciudad", "la colonia")
        self.mensaje = f"Tu solicitud para unirte a {ciudad_colonia} ha sido aceptada."

class EventoSolicitudColoniaRechazada(EventoBase):
    def __init__(self, datos, receptores):
        super().__init__(TipoEvento.SOLICITUD_COLONIA_RECHAZADA, datos, receptores)

    def construir_mensaje(self) -> str:
        ciudad_colonia = self.datos.get("colonia_ciudad", "la colonia")
        self.mensaje = f"Tu solicitud para unirte a {ciudad_colonia} ha sido rechazada."

class EventoDesactivarColonia(EventoBase):
    def __init__(self, datos, receptores):
        super().__init__(TipoEvento.DESACTIVAR_COLONIA, datos, receptores)

    def construir_mensaje(self) -> str:
        ciudad_colonia = self.datos.get("colonia_ciudad", "la colonia")
        self.mensaje = f"La colonia {ciudad_colonia} ha sido desactivada."


class EventoEstablecerLiderColonia(EventoBase):
    def __init__(self, datos, receptores):
        super().__init__(TipoEvento.ESTABLER_LIDER_COLONIA, datos, receptores)

    def construir_mensaje(self) -> str:
        ciudad_colonia = self.datos.get("colonia_ciudad", "la colonia")
        self.mensaje = f"Has sido designado como líder de {ciudad_colonia}."

class EventoEliminarLiderColonia(EventoBase):
    def __init__(self, datos, receptores):
        super().__init__(TipoEvento.ELIMINAR_LIDER_COLONIA, datos, receptores)

    def construir_mensaje(self) -> str:
        ciudad_colonia = self.datos.get("colonia_ciudad", "la colonia")
        self.mensaje = f"Tu rol de líder en {ciudad_colonia} ha sido revocado."

class EventoRegistroGrupoRetorno(EventoBase):
    def __init__(self, datos, receptores):
        super().__init__(TipoEvento.REGISTRO_GRUPO_RETORNO, datos, receptores)

    def construir_mensaje(self) -> str:
        retorno_anio = self.datos.get("retorno_anio", "el retorno")
        self.mensaje = f"Tu grupo de retorno se ha registrado exitosamente en {retorno_anio}."
    
class EventoActualizacionRegistroGrupo(EventoBase):
    def __init__(self, datos, receptores):
        super().__init__(TipoEvento.ACTUALIZACION_REGISTRO_GRUPO, datos, receptores)

    def construir_mensaje(self) -> str:
        retorno_anio = self.datos.get("retorno_anio", "el retorno")
        self.mensaje = f"El registro de tu grupo de retorno ha sido actualizado en {retorno_anio}."

class EventoDarseBajaGrupo(EventoBase):
    def __init__(self, datos, receptores):
        super().__init__(TipoEvento.DARSE_BAJA_GRUPO, datos, receptores)

    def construir_mensaje(self) -> str:
        nombre_usuario = self.datos.get("nombre_usuario", "el usuario")
        apellido_usuario = self.datos.get("apellido_usuario", "")
        nombre_completo = f"{nombre_usuario} {apellido_usuario}".strip()
        self.mensaje = f"El usuario {nombre_completo} se ha dado de baja del grupo de retorno."

class EventoEliminarGrupoRetorno(EventoBase):
    def __init__(self, datos, receptores):
        super().__init__(TipoEvento.ELIMINAR_GRUPO_RETORNO, datos, receptores)

    def construir_mensaje(self) -> str:
        lider = self.datos.get("lider", "el grupo de retorno")
        self.mensaje = f"El lider del grupo {lider} ha eliminado el grupo de retorno."

class EventoDarseBajaRetorno(EventoBase):
    def __init__(self, datos, receptores):
        super().__init__(TipoEvento.DARSE_BAJA_RETORNO, datos, receptores)

    def construir_mensaje(self) -> str:
        nombre_usuario = self.datos.get("nombre_usuario", "el usuario")
        apellido_usuario = self.datos.get("apellido_usuario", "")
        nombre_completo = f"{nombre_usuario} {apellido_usuario}".strip()
        retorno_anio = self.datos.get("retorno_anio", "el retorno")
        self.mensaje = f"El usuario {nombre_completo} se ha dado de baja del retorno {retorno_anio}."
