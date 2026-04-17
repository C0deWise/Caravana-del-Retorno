"""
    retorno_grupo_usuario_modelo.py define el modelo que representa la relación entre usuarios y grupos de retorno. 
    Este  gestiona la participación de los usuarios en los grupos de retorno, permitiendo asignar múltiples usuarios a un mismo grupo. 
"""


from sqlalchemy import ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.retornos.modelos.grupo_retorno_modelo import GrupoRetorno
from app.usuarios.models.usuario import Usuario


class RetornoGrupoUsuario:
    __tablename__ = 'usuario_grupo_retorno'
    ugr_codigo: Mapped[int] = mapped_column("ugr_codigo", Integer, primary_key=True, autoincrement=True)
    us_codigo: Mapped[int] = mapped_column("us_codigo", Integer, ForeignKey("usuario.us_codigo"), nullable=False)
    gr_codigo: Mapped[int] = mapped_column("gr_codigo", Integer, ForeignKey("grupo_retorno.gr_codigo"), nullable=False)

    # ─────────────────────────────────────────
    #  Relaciones
    # ─────────────────────────────────────────
    usuario: Mapped["Usuario"] = relationship(Usuario)
    grupo: Mapped["GrupoRetorno"] = relationship("GrupoRetorno") 

    __table_args__ = (
        UniqueConstraint("us_codigo", "gr_codigo", name="uk1_uk2_usuario_grupo_retorno"),
    )
    def __repr__(self) -> str:
        """Representación en cadena del objeto RetornoGrupoUsuario."""
        return (
            f"RetornoGrupoUsuario(ugr_codigo={self.ugr_codigo!r}, us_codigo={self.us_codigo!r}, gr_codigo={self.gr_codigo!r})"
        )