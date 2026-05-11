from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from typing import Literal

from app.multimedia.modelos.multimedia_modelo import TipoMultimedia, FormatoMultimedia

class MultimediaCrear(BaseModel):
    publicacion: int = Field(..., gt=0, description="ID de la publicación a la que pertenece el multimedia")
    tipo: TipoMultimedia = Field(..., description="Tipo de archivo multimedia")
    formato: FormatoMultimedia = Field(..., description="Formato del archivo multimedia")
    url: str = Field(..., description="URL del archivo multimedia")
    descripcion: str = Field(..., description="Descripción del archivo multimedia")

    model_config = {"from_attributes": True}

class MultimediaRespuesta(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    codigo: int
    publicacion: int
    tipo: TipoMultimedia
    formato: FormatoMultimedia
    url: str
    descripcion: str

class MultimediaCargar(BaseModel):
    publicacion_id: int = Field(..., gt=0, description="ID de la publicación a la que se asociará el multimedia")
    archivos: list[str] = Field(..., description="Lista de URLs de los archivos multimedia a cargar")

    model_config = {"from_attributes": True}

class MultimediaRespuestaCargar(BaseModel):
    publicacion_id: int
    mensaje: str
    cantidad_archivos_cargados: int
    multimedia: list[MultimediaRespuesta]

    model_config = {"from_attributes": True}