"""
Modulo de modelos para la gestión de publicaciones en la aplicación. Contiene la clase Publicacion, que representa
la entidad de una publicación en la base de datos. Esta clase define los atributos de una publicación, como su código,
retorno asociado, autor, reseña, título, fecha de creación y la relación con los archivos multimedia asociados a la 
publicación.
"""

from sqlalchemy import Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime

from app.core.database import Base
from app.multimedia.modelos.multimedia_modelo import Multimedia

class Publicacion (Base):
    __tablename__ = "publicacion"

    codigo: Mapped[int] = mapped_column("pu_codigo", Integer, primary_key=True, autoincrement=True)
    retorno: Mapped[int] = mapped_column("re_codigo", Integer, ForeignKey("retorno.codigo"), nullable=False)
    autor: Mapped[int] = mapped_column("us_codigo_autor", Integer, ForeignKey("usuario.us_codigo"), nullable=False)
    resena: Mapped[str] = mapped_column("pu_resena", String(1000), nullable=True)
    titulo: Mapped[str] = mapped_column("pu_titulo", String(255), nullable=False)
    fecha_creacion: Mapped[datetime] = mapped_column("pu_fecha_creacion", DateTime, default=datetime.utcnow)

    multimedia_lista: Mapped[list["Multimedia"]] = relationship(
        "Multimedia", 
        back_populates="publicacion_ref",
        cascade="all, delete-orphan")
    autor_ref = relationship("Usuario", foreign_keys=[autor])

    @property
    def nombre_autor(self) -> str | None:
        if not self.autor_ref:
            return None
        return f"{self.autor_ref.us_nombre} {self.autor_ref.us_apellido}".strip()

    def __repr__(self) -> str:
        """Representación en cadena del objeto Publicacion."""
        return (
            f"Publicacion(codigo={self.codigo!r}, titulo={self.titulo!r}, "
            f"resena={self.resena!r}, fecha_creacion={self.fecha_creacion!r})"
        )