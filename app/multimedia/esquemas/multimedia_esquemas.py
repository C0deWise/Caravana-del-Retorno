"""
Modulo de esquemas para la gestión de multimedia en la aplicación. Contiene las clases de esquemas que se utilizan
para validar y serializar los datos relacionados con los archivos multimedia, como la creación de nuevos registros
de multimedia y la respuesta al cargar multimedia. Estos esquemas permiten garantizar la integridad de los datos y 
proporcionar respuestas consistentes a los clientes de la API.
"""

from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from typing import Literal

from app.multimedia.modelos.multimedia_modelo import TipoMultimedia, FormatoMultimedia

class MultimediaCrear(BaseModel):
    """Esquema para la creación de un nuevo registro de multimedia."""
    publicacion: int = Field(..., gt=0, description="ID de la publicación a la que pertenece el multimedia")
    tipo: TipoMultimedia = Field(..., description="Tipo de archivo multimedia")
    formato: FormatoMultimedia = Field(..., description="Formato del archivo multimedia")
    url: str = Field(..., description="URL del archivo multimedia")
    descripcion: str = Field(..., description="Descripción del archivo multimedia")

    model_config = {"from_attributes": True}

class MultimediaRespuesta(BaseModel):
    """Esquema para la respuesta al consultar un registro de multimedia."""
    model_config = ConfigDict(from_attributes=True)
    
    codigo: int
    publicacion: int
    tipo: TipoMultimedia
    formato: FormatoMultimedia
    url: str
    descripcion: str