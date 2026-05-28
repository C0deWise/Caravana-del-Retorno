"""
Este módulo define los modelos de datos para las entidades `Usuario` y `Rol` utilizando SQLAlchemy.
Establece la estructura de las tablas en la base de datos, incluyendo columnas,
tipos de datos, relaciones y constraints para garantizar la integridad de los datos.
"""

import enum
from sqlalchemy import Integer, String, Date, ForeignKey, Enum, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.colonias.models.colonia_model import Colonia
from app.core.database import Base


class Rol(Base):
    """
    Modelo que representa los roles de usuario en el sistema.
    Permite diferenciar los niveles de acceso y permisos.
    """
    __tablename__ = "rol"

    ro_codigo: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ro_nombre: Mapped[str] = mapped_column(String, nullable=False, unique=True)

    def __repr__(self) -> str:
        """Representación en cadena del objeto Rol."""
        return f"Rol(ro_codigo={self.ro_codigo!r}, ro_nombre={self.ro_nombre!r})"


class TipoDoc(str, enum.Enum):
    """Enumeración para los tipos de documento de identidad."""
    CC = "CC"
    CE = "CE"


class Genero(str, enum.Enum):
    """Enumeración para el género de los usuarios."""
    F = "F"
    M = "M"
    OTRO = "otro"


class Usuario(Base):
    """
    Modelo que representa a un usuario en el sistema.
    Contiene su información personal, credenciales y relaciones con otras entidades.
    """
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
    colonia: Mapped["Colonia"] = relationship(Colonia)
    rol: Mapped["Rol"] = relationship("Rol")

    def __repr__(self) -> str:
        """Representación en cadena del objeto Usuario."""
        return (
            f"Usuario(us_codigo={self.us_codigo!r}, us_documento={self.us_documento!r}, "
            f"us_nombre={self.us_nombre!r}, us_apellido={self.us_apellido!r})"
        )