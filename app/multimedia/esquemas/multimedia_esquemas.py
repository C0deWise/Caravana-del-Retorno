from pydantic import BaseModel, Field
from datetime import datetime
from typing import Literal

from app.multimedia.config import TipoMultimedia

class MultimediaCrear(BaseModel):
    retorno: int
    tipo: TipoMultimedia
    url: str
    nombre_archivo: str

    model_config = {"from_attributes": True}

class MultimediaRespuesta(BaseModel):
    codigo: int
    retorno: int
    tipo: TipoMultimedia
    url: str
    nombre_archivo: str
    fecha_creacion: datetime

    model_config = {"from_attributes": True}