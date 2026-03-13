from datetime import datetime
import enum
from typing import Optional

from pydantic import BaseModel

from app.colonias.models.solicitud_colonia import EstadoSolicitud  # ajusta según tu proyecto


class EstadoSolicitudSchema(str, enum.Enum):
    aceptada = "aceptada"
    rechazada = "rechazada"

class SolicitudColoniaBase(BaseModel):
    us_codigo: int
    co_codigo: int


class SolicitudColoniaCrear(SolicitudColoniaBase):
    """El estado y la fecha se asignan automáticamente; no se reciben del cliente."""
    pass



class SolicitudColoniaUpdate(BaseModel):
    so_estado: Optional[EstadoSolicitudSchema] = None


class SolicitudColoniaResponse(SolicitudColoniaBase):
    so_codigo: int
    so_estado: EstadoSolicitud
    so_fecha_creacion: datetime

    model_config = {"from_attributes": True}