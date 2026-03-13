"""
    usuario.py define el modelo de datos para los usuarios, incluyendo sus atributos y relaciones.
"""

import enum
from sqlalchemy import Integer, String, Date, ForeignKey, Enum, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.colonias.models.colonia import Colonia
from app.core.database import Base


class Rol(Base):
    __tablename__ = "rol"

    ro_codigo: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ro_nombre: Mapped[str] = mapped_column(String, nullable=False, unique=True)

    def __repr__(self) -> str:
        return f"Rol(id={self.id!r}, ro_nombre={self.ro_nombre!r})"
    

class TipoDoc(str, enum.Enum):
    CC = "CC"
    CE = "CE"


class Genero(str, enum.Enum):
    F = "F"
    M = "M"
    OTRO = "otro"


class Usuario(Base):
    __tablename__ = "usuario"

    us_codigo: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    us_fecha_creacion: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    us_tipo_doc: Mapped[TipoDoc] = mapped_column(Enum(TipoDoc), nullable=False)
    us_documento: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    us_celular: Mapped[str] = mapped_column(String, nullable=False,unique=True)
    us_correo: Mapped[str] = mapped_column(String, nullable=False,unique=True)
    us_contrasenia: Mapped[str] = mapped_column(String, nullable=False)
    co_codigo: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("colonia.co_codigo"), nullable=True
    )
    ro_codigo: Mapped[int] = mapped_column(
        Integer, ForeignKey("rol.ro_codigo"), nullable=False, default=1
    )

    us_nombre: Mapped[str] = mapped_column(String, nullable=False)
    us_apellido: Mapped[str] = mapped_column(String, nullable=False)
    us_genero: Mapped[Genero] = mapped_column(Enum(Genero), nullable=False)
    us_fecha_nacimiento: Mapped[Date] = mapped_column(Date, nullable=False)

    us_pais: Mapped[str] = mapped_column(String, nullable=False)
    us_departamento: Mapped[str | None] = mapped_column(String, nullable=True)
    us_ciudad: Mapped[str | None] = mapped_column(String, nullable=True)

    # ─────────────────────────────────────────
    #  Relaciones
    # ─────────────────────────────────────────
    colonia: Mapped["Colonia"] = relationship("Colonia")
    rol: Mapped["Rol"] = relationship("Rol")

    def __repr__(self) -> str:
        return (
            f"Usuario(id={self.id!r}, us_documento={self.us_documento!r}, "
            f"us_nombre={self.us_nombre!r}, us_apellido={self.us_apellido!r})"
        )
