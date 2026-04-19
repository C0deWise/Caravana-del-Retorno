"""
Módulo que define el modelo de datos para la entidad Colonia.
Contiene la clase Colonia que representa la estructura de la tabla de colonias
en la base de datos, incluyendo sus atributos y tipos de datos.
"""
import enum

from sqlalchemy import Integer, String, Enum
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class ColoniaEstado(str, enum.Enum):
    ACTIVA = "activa"
    INACTIVA = "inactiva"

class Colonia(Base):
    __tablename__ = "colonia"

    codigo: Mapped[int] = mapped_column("co_codigo", Integer, primary_key=True, autoincrement=True)
    pais: Mapped[str] = mapped_column("co_pais", String, nullable=False)
    departamento: Mapped[str | None] = mapped_column("co_departamento", String, nullable=True)
    ciudad: Mapped[str | None] = mapped_column("co_ciudad", String, nullable=True)
    estado: Mapped[ColoniaEstado] = mapped_column("co_estado", Enum(ColoniaEstado), nullable=False, default=ColoniaEstado.ACTIVA)
    lider: Mapped[int | None] = mapped_column("lider_id", Integer, nullable=True)

    def __repr__(self) -> str:
        return (
            f"Colonia(id={self.codigo!r}, pais={self.pais!r}, "
            f"departamento={self.departamento!r}, ciudad={self.ciudad!r}, estado={self.estado!r}, lider={self.lider!r})"
        )