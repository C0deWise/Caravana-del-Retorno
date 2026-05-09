"""
    persona_grupo_retorno_modelo.py define el modelo que representa la relación entre personas y grupos de retorno. 
    Este  gestiona la participación de las personas en los grupos de retorno, permitiendo asignar múltiples personas a un mismo grupo. 
"""


from sqlalchemy import ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.retornos.modelos.grupo_retorno_modelo import GrupoRetorno
from app.retornos.modelos.persona_modelo import Persona



class persona_grupo_retorno(Base):
    __tablename__ = 'persona_grupo_retorno'
    pgr_codigo: Mapped[int] = mapped_column("pgr_codigo", Integer, primary_key=True, autoincrement=True)
    pe_codigo: Mapped[int] = mapped_column("pe_codigo", Integer, ForeignKey("persona.pe_codigo"), nullable=False)
    gr_codigo: Mapped[int] = mapped_column("gr_codigo", Integer, ForeignKey("grupo_retorno.gr_codigo"), nullable=False)


    #  Relaciones

    persona: Mapped["Persona"] = relationship("Persona")
    grupo: Mapped["GrupoRetorno"] = relationship("GrupoRetorno") 

    __table_args__ = (
        UniqueConstraint("pe_codigo", "gr_codigo", name="uk1_uk2_persona_grupo_retorno"),
    )
    def __repr__(self) -> str:
        """Representación en cadena del objeto persona_grupo_retorno."""
        return (
            f"persona_grupo_retorno(pgr_codigo={self.pgr_codigo!r}, pe_codigo={self.pe_codigo!r}, gr_codigo={self.gr_codigo!r})"
        )