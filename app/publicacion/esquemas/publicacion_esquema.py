"""
Modulo de esquemas para la gestión de publicaciones en la aplicación. Contiene las clases de esquema que se utilizan
para validar los datos de entrada y salida relacionados con las publicaciones. Estos esquemas se utilizan en los 
endpoints de la API para garantizar que los datos recibidos y enviados cumplan con las estructuras esperadas, facilitando
la interacción con los clientes de la API y asegurando la integridad de los datos.
"""

from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime

from app.multimedia.esquemas.multimedia_esquemas import MultimediaRespuesta

class PublicacionCrear(BaseModel):
    """Esquema para la creación de una nueva publicación."""
    retorno: int = Field(..., gt=0, description="Código del retorno asociado a la publicación")
    autor: int = Field(..., gt=0, description="ID del autor de la publicación")
    titulo: str = Field(..., description="Título de la publicación")
    resena: str = Field(..., description="Reseña de la publicación")

    model_config = {"from_attributes": True}

class PublicacionRespuesta(BaseModel):
    """Esquema para la respuesta de una publicación, incluyendo los archivos multimedia asociados."""
    model_config = ConfigDict(from_attributes=True)

    codigo: int
    retorno: int
    autor: int
    nombre_autor: str | None = None
    titulo: str
    resena: str
    fecha_creacion: datetime
    multimedia_lista: list[MultimediaRespuesta] = []

class PublicacionEditar(BaseModel):
    """Esquema para la edición de una publicación existente."""
    retorno: int | None = Field(None, gt=0, description="Nuevo código del retorno asociado a la publicación")
    titulo: str | None = Field(None, description="Nuevo título de la publicación")
    resena: str | None = Field(None, description="Nueva reseña de la publicación")
    archivos_eliminar: list[int] | None = None

    model_config = ConfigDict(from_attributes=True)