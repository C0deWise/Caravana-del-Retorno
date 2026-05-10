"""
    solicitud_grupo_retorno_modelo.py Modelo de datos para las solicitudes de grupos de retorno a usuarios.
"""




from sqlalchemy import ForeignKey, Integer, DateTime, Enum, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.retornos.modelos.grupo_retorno_modelo import GrupoRetorno
from app.usuarios.models.usuario import Usuario
from app.retornos.esquemas.solicitud_grupo_retorno_esquema import SolicitudGrupoRetornoEstado

class SolicitudGrupoRetorno(Base):
    __tablename__ = 'solicitud_grupo_retorno'

    solgr_codigo: Mapped[int] = mapped_column("solgr_codigo", Integer, primary_key=True, autoincrement=True)
    us_codigo: Mapped[int] = mapped_column("us_codigo", Integer, ForeignKey("usuario.us_codigo"), nullable=False)
    gr_codigo: Mapped[int] = mapped_column("gr_codigo", Integer, ForeignKey("grupo_retorno.gr_codigo"), nullable=False)
    solgr_time_stamp: Mapped[DateTime] = mapped_column(
        "solgr_time_stamp",
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    solgr_estado: Mapped[SolicitudGrupoRetornoEstado] = mapped_column(
        "solgr_estado",
        Enum(SolicitudGrupoRetornoEstado),
        nullable=False,
        default=SolicitudGrupoRetornoEstado.PENDIENTE,
    )

    #---Relaciones---# 
    usuario: Mapped["Usuario"] = relationship("Usuario")
    grupo: Mapped["GrupoRetorno"] = relationship("GrupoRetorno")

    def __repr__(self) -> str:
        """Representación en cadena del objeto SolicitudGrupoRetorno."""
        return (
            f"SolicitudGrupoRetorno(solgr_codigo={self.solgr_codigo!r}, us_codigo={self.us_codigo!r}, "
            f"gr_codigo={self.gr_codigo!r}, solgr_time_stamp={self.solgr_time_stamp!r}, "
            f"solgr_estado={self.solgr_estado!r})"
        )