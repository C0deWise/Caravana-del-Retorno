"""
    registro_retorno_grupo_modelo.py define el modelo que representa la relación entre grupos de retorno y retornos.
"""


from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.retornos.modelos.grupo_retorno_modelo import GrupoRetorno
from app.retornos.modelos.retorno_modelo import Retorno
from app.core.database import Base

class RegistroRetornoGrupo(Base):
    __tablename__ = 'registro_retorno_grupo'
    regg_codigo: Mapped[int] = mapped_column("regg_codigo",Integer, primary_key=True, autoincrement=True)
    gr_codigo: Mapped[int] = mapped_column("gr_codigo", Integer, ForeignKey("grupo_retorno.gr_codigo"), nullable=False)
    re_codigo: Mapped[int] = mapped_column("re_codigo", Integer, ForeignKey("retorno.codigo"), nullable=False)
    reggr_num_hospedaje: Mapped[int] = mapped_column("reggr_num_hospedaje", Integer, nullable=False, default=0)
    reggr_num_transporte: Mapped[int] = mapped_column("reggr_num_transporte", Integer, nullable=False, default=0)
    reggr_num_parqueadero: Mapped[int] = mapped_column("reggr_num_parqueadero", Integer, nullable=False, default=0)
    reggr_anotacion: Mapped[str] = mapped_column("reggr_anotacion", String(500), nullable=True)
    

    # ─────────────────────────────────────────
    #  Relaciones
    # ─────────────────────────────────────────
    retorno: Mapped["Retorno"] = relationship(Retorno)
    grupo_retorno: Mapped["GrupoRetorno"] = relationship(GrupoRetorno)

    def __repr__(self) -> str:
        """Representación en cadena del objeto RegistroRetornoGrupo."""
        return (
            f"RegistroRetornoGrupo(regg_codigo={self.regg_codigo!r}, gr_codigo={self.gr_codigo!r}, "
            f"re_codigo={self.re_codigo!r}, reggr_num_hospedaje={self.reggr_num_hospedaje!r}, "
            f"reggr_num_transporte={self.reggr_num_transporte!r}, reggr_num_parqueadero={self.reggr_num_parqueadero!r}, "
            f"reggr_anotacion={self.reggr_anotacion!r})"
        )

