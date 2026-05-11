from sqlalchemy import Integer, String, DateTime, ForeignKey, Enum
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

    def __repr__(self) -> str:
        """Representación en cadena del objeto Publicacion."""
        return (
            f"Publicacion(codigo={self.codigo!r}, titulo={self.titulo!r}, "
            f"resena={self.resena!r}, fecha_creacion={self.fecha_creacion!r})"
        )