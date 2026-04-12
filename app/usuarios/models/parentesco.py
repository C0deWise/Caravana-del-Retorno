"""
    parentesco.py define el modelo de datos para las relaciones de parentesco entre usuarios.
"""

import enum
from sqlalchemy import Integer, String, Date, ForeignKey, Enum, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.colonias.models.colonia_model import Colonia
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

    codigo: Mapped[int] = mapped_column("pa_codigo", Integer, primary_key=True, autoincrement=True)
    fecha_creacion: Mapped[DateTime] = mapped_column(
        "pa_fecha_creacion",
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    estado: Mapped[EstadoSolicitudParentesco] = mapped_column("pa_estado", Enum(EstadoSolicitudParentesco), nullable=False, default=EstadoSolicitudParentesco.pendiente)

    codigo_solicitante: Mapped[int] = mapped_column("us_codigo_solicitante", Integer, ForeignKey("usuario.us_codigo"), nullable=False)
    codigo_destinatario: Mapped[int] = mapped_column("us_codigo_destinatario", Integer, ForeignKey("usuario.us_codigo"), nullable=False)

    tipo_parentesco: Mapped[TipoParentesco] = mapped_column("pa_tipo_parentesco", Enum(TipoParentesco), nullable=False)

    # ─────────────────────────────────────────
    #  Relaciones
    # ─────────────────────────────────────────
    solicitante: Mapped["Usuario"] = relationship("Usuario", foreign_keys=[codigo_solicitante])
    destinatario: Mapped["Usuario"] = relationship("Usuario", foreign_keys=[codigo_destinatario])

    def __repr__(self) -> str:
        return f"Parentesco(id={self.pa_codigo!r}, pa_estado={self.pa_estado!r} us_codigo_solicitante={self.us_codigo_solicitante!r} us_codigo_destinatario={self.us_codigo_destinatario!r} tipo_parentesco={self.pa_tipo_parentesco!r})"