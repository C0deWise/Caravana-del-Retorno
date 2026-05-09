"""
    persona_modelo.py Modelo de datos para las personas que no son usuarios del sistema, pero asisten a un retorno
    mediante los grupos de retorno.
"""



import enum

from sqlalchemy import Enum, Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base


class TipoDoc(str, enum.Enum):
    """Enumeración para los tipos de documento de identidad."""
    CC = "CC"
    CE = "CE"

class Persona(Base):
    __tablename__ = 'persona'
    pe_codigo: Mapped[int] = mapped_column("pe_codigo", Integer, primary_key=True, autoincrement=True)
    pe_tipo_doc: Mapped[TipoDoc] = mapped_column(Enum(TipoDoc), nullable=False)
    pe_documento: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    pe_nombre: Mapped[str] = mapped_column("pe_nombre", String(100), nullable=False)
    pe_apellido: Mapped[str] = mapped_column("pe_apellido", String(100), nullable=False)
    pe_correo: Mapped[str] = mapped_column("pe_correo", String(100), unique=True, nullable=True)
    pe_fecha_nacimiento: Mapped[str] = mapped_column("pe_fecha_nacimiento", String(100), nullable=False)


    def __repr__(self) -> str:
        """Representación en cadena del objeto Persona."""
        return (
            f"Persona(pe_codigo={self.pe_codigo!r}, pe_nombre={self.pe_nombre!r}, "
            f"pe_apellido={self.pe_apellido!r}, pe_correo={self.pe_correo!r}, "
            f"pe_fecha_nacimiento={self.pe_fecha_nacimiento!r})"
        )