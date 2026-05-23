



from pydantic import BaseModel


class NotificacionCrear(BaseModel):
    no_mensaje: str
    codigo_receptor: int
    codigo_evento: int

class Evento(BaseModel):
    codigo: int
    nombre: str
    descripcion: str
class NotificacionRespuesta(BaseModel):
    codigo: int
    mensaje: str
    codigo_receptor: int
    evento: Evento
    time_stamp: str
    estado: str

class NotificacionCrearLote(BaseModel):
    no_mensaje: str
    codigo_receptores: list[int]
    codigo_evento: int

class EventoCrear(BaseModel):
    nombre: str
    descripcion: str    