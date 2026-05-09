from datetime import datetime
import enum
from typing import Optional

from pydantic import BaseModel

from app.colonias.models.solicitud_colonia import EstadoSolicitud  # ajusta según tu proyecto


class EstadoSolicitudSchema(str, enum.Enum):
    aceptada = "aceptada"
    rechazada = "rechazada"



class SolicitudColoniaCrear(BaseModel):
    """El estado y la fecha se asignan automáticamente; no se reciben del cliente."""
    codigo_usuario: int
    codigo_colonia: int



class SolicitudColoniaUpdate(BaseModel):
    so_estado: Optional[EstadoSolicitudSchema] = None

class MiembroRegistradoColoniaRespuesta(BaseModel):
    codigo_usuario: int
    nombre_usuario: str
    apellido_usuario: str
    codigo_colonia: int 
class SolicitudColoniaRespuesta(BaseModel):
    codigo: int
    estado: EstadoSolicitud
    fecha_creacion: datetime
    codigo_usuario: int
    nombre_usuario: str
    apellido_usuario: str
    codigo_colonia: int
