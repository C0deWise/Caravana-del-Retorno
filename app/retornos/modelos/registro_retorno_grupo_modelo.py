"""
    registro_retorno_grupo_modelo.py define el modelo que representa la relación entre grupos de retorno y retornos.
"""


from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.retornos.modelos.grupo_retorno_modelo import GrupoRetorno
from app.retornos.modelos.retorno_modelo import Retorno


class RegistroRetornoGrupo(Base):
    __tablename__ = 'registro_retorno_grupo'
    regg_codigo: Mapped[int] = mapped_column("regg_codigo",Integer, primary_key=True, autoincrement=True)
    cod_grupo: Mapped[int] = mapped_column("gr_codigo", Integer, ForeignKey("grupo_retorno.gr_codigo"), nullable=False)
    retorno: Mapped[int] = mapped_column("re_codigo", Integer, ForeignKey("retorno.codigo"), nullable=False)
    num_hospedaje: Mapped[int] = mapped_column("reggr_num_hospedaje", Integer, nullable=False, default=0)
    num_transporte: Mapped[int] = mapped_column("reggr_num_transporte", Integer, nullable=False, default=0)
    num_parqueadero: Mapped[int] = mapped_column("reggr_num_parqueadero", Integer, nullable=False, default=0)
    anotacion: Mapped[str] = mapped_column("reggr_anotacion", String(500), nullable=True)
    


    #  Relaciones
    # ─────────────────────────────────────────
    retorno_rel: Mapped["Retorno"] = relationship(Retorno)
    grupo_retorno_rel: Mapped["GrupoRetorno"] = relationship(GrupoRetorno)

    def __repr__(self) -> str:
        """Representación en cadena del objeto RegistroRetornoGrupo."""
        return (
            f"RegistroRetornoGrupo(regg_codigo={self.regg_codigo!r}, cod_grupo={self.cod_grupo!r}, "
            f"retorno={self.retorno!r}, num_hospedaje={self.num_hospedaje!r}, "
            f"num_transporte={self.num_transporte!r}, num_parqueadero={self.num_parqueadero!r}, "
            f"anotacion={self.anotacion!r})"
        )
