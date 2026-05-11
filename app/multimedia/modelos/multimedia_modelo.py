"""
Modulo de modelos para la gestión de multimedia en la aplicación. Contiene la clase Multimedia, que representa
un archivo multimedia asociado a una publicación específica, con atributos como tipo, formato, URL y descripción.
También se definen los enumerados TipoMultimedia y FormatoMultimedia para restringir los valores permitidos en los
campos correspondientes.
"""

import enum

from sqlalchemy import Integer, String, DateTime, ForeignKey
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime

from app.core.database import Base

class TipoMultimedia(str, enum.Enum):
    IMAGEN = "imagen"
    VIDEO = "video"
    DOCUMENTO = "documento"
class FormatoMultimedia(str, enum.Enum):
    JPG = "jpg"
    JPEG = "jpeg"
    PNG = "png"
    GIF = "gif"
    MP4 = "mp4"
    AVI = "avi"
    MOV = "mov"
    MKV = "mkv"
    PDF = "pdf"
    EMBED = "embed"

class Multimedia(Base):
    __tablename__ = "multimedia"

    codigo: Mapped[int] = mapped_column("mu_codigo", Integer, primary_key=True, autoincrement=True)
    publicacion: Mapped[int] = mapped_column("pu_codigo", Integer, ForeignKey("publicacion.pu_codigo"), nullable=False)
    tipo: Mapped[TipoMultimedia] = mapped_column("mu_tipo", SQLEnum(TipoMultimedia, name="tipomultimedia", create_type=True), nullable=False)
    formato: Mapped[FormatoMultimedia] = mapped_column("mu_formato", SQLEnum(FormatoMultimedia, name="formatomultimedia", create_type=True), nullable=False)
    url: Mapped[str] = mapped_column("mu_url", String(500), nullable=False)
    descripcion: Mapped[str] = mapped_column("mu_descripcion", String(255), nullable=False)

    publicacion_ref: Mapped["Publicacion"] = relationship(
        "Publicacion", 
        back_populates="multimedia_lista"
    )

    def __repr__(self) -> str:
        """Representación en cadena del objeto Multimedia."""
        return (
            f"Multimedia(codigo={self.codigo!r}, publicacion={self.publicacion!r}, "
            f"tipo={self.tipo!r}, formato={self.formato!r}, url={self.url!r}, "
            f"descripcion={self.descripcion!r})"
        )