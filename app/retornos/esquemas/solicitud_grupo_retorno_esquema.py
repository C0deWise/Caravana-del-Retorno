from enum import Enum
from pydantic import BaseModel, Field
from datetime import datetime

class SolicitudGrupoRetornoEstado(str, Enum):
    PENDIENTE = "pendiente"
    ACEPTADO = "aceptado"
    RECHAZADO = "rechazado"
    EXPIRADO = "expirado"

class SolicitudGrupoRetornoRespuesta(BaseModel):
    solgr_codigo: int = Field(alias="solgr_codigo")
    us_codigo: int = Field(alias="us_codigo")
    gr_codigo: int = Field(alias="gr_codigo")
    solgr_time_stamp: datetime = Field(alias="solgr_time_stamp")
    solgr_estado: SolicitudGrupoRetornoEstado = Field(alias="solgr_estado")

    model_config = {"from_attributes": True, "populate_by_name": True}
