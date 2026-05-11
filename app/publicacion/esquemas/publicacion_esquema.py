from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime

from app.multimedia.esquemas.multimedia_esquemas import MultimediaRespuesta

class PublicacionCrear(BaseModel):
    retorno: int = Field(..., gt=0, description="Código del retorno asociado a la publicación")
    autor: int = Field(..., gt=0, description="ID del autor de la publicación")
    titulo: str = Field(..., description="Título de la publicación")
    resena: str = Field(..., description="Reseña de la publicación")

    model_config = {"from_attributes": True}

class PublicacionRespuesta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    codigo: int
    retorno: int
    autor: int
    titulo: str
    resena: str
    fecha_creacion: datetime
    multimedia_lista: list[MultimediaRespuesta] = []