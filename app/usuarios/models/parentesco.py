"""
    parentesco.py define el modelo de datos para las relaciones de parentesco entre usuarios.
"""

import enum
from sqlalchemy import Integer, String, Date, ForeignKey, Enum, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.colonias.models.colonia import Colonia
from app.core.database import Base
from app.usuarios.models.usuario import Rol, Usuario


class EstadoSolicitudParentesco(str, enum.Enum):
    pendiente = "pendiente"
    aceptada = "aceptada"
    rechazada = "rechazada"
    expirada = "expirada"

class TipoParentesco(str, enum.Enum):
    padre = "padre"
    madre = "madre"
    hermano = "hermano (a)"
    hijo = "hijo (a)"
    abuelo = "abuelo (a)"
    tio = "tio (a)"
    primo = "primo (a)"
    madrastra = "madrastra"
    padrastro = "padrastro"
    hijastro = "hijastro (a)"
    conyuge = "conyuge"

class Parentesco(Base):
    __tablename__ = "parentesco"

    pa_codigo: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    pa_fecha_creacion: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    pa_estado: Mapped[EstadoSolicitudParentesco] = mapped_column(Enum(EstadoSolicitudParentesco), nullable=False, default=EstadoSolicitudParentesco.pendiente)

    us_codigo_solicitante: Mapped[int] = mapped_column(Integer, ForeignKey("usuario.us_codigo"), nullable=False)
    us_codigo_destinatario: Mapped[int] = mapped_column(Integer, ForeignKey("usuario.us_codigo"), nullable=False)

    pa_tipo_parentesco: Mapped[TipoParentesco] = mapped_column(Enum(TipoParentesco), nullable=False)

    # ─────────────────────────────────────────
    #  Relaciones
    # ─────────────────────────────────────────
    solicitante: Mapped["Usuario"] = relationship("Usuario", foreign_keys=[us_codigo_solicitante])
    destinatario: Mapped["Usuario"] = relationship("Usuario", foreign_keys=[us_codigo_destinatario])

    def __repr__(self) -> str:
        return f"Parentesco(id={self.pa_codigo!r}, pa_estado={self.pa_estado!r} us_codigo_solicitante={self.us_codigo_solicitante!r} us_codigo_destinatario={self.us_codigo_destinatario!r} tipo_parentesco={self.pa_tipo_parentesco!r})"