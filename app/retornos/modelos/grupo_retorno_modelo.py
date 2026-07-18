"""
 grupo_retorno.py define el modelo que representa grupos de asistentes a un retorno. El proposito de este modelo
 es organizar a los usuarios que desean asistir a un retorno bajo un mismo grupo.
   
"""

from sqlalchemy import Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from app.usuarios.models.usuario import Usuario

class GrupoRetorno(Base):
    __tablename__ = 'grupo_retorno'
    gr_codigo: Mapped[int] = mapped_column("gr_codigo",Integer, primary_key=True, autoincrement=True)
    us_codigo_lider: Mapped[int] = mapped_column("us_codigo_lider", Integer, ForeignKey("usuario.us_codigo"), nullable=False)

    # ─────────────────────────────────────────
    #  Relaciones
    # ─────────────────────────────────────────
    lider: Mapped["Usuario"] = relationship(Usuario)    
    # Relaciones inversas con cascade delete para eliminación en cascada
    miembros: Mapped[list["persona_grupo_retorno"]] = relationship(
        "persona_grupo_retorno",
        cascade="all, delete-orphan",
        back_populates="grupo"
    )
    solicitudes: Mapped[list["SolicitudGrupoRetorno"]] = relationship(
        "SolicitudGrupoRetorno",
        cascade="all, delete-orphan",
        back_populates="grupo"
    )
    registros_retornos: Mapped[list["RegistroRetornoGrupo"]] = relationship(
        "RegistroRetornoGrupo",
        cascade="all, delete-orphan",
        back_populates="grupo_retorno_rel"
    )
    usuarios: Mapped[list["RetornoGrupoUsuario"]] = relationship(
        "RetornoGrupoUsuario",
        cascade="all, delete-orphan",
        back_populates="grupo"
    )
    def __repr__(self) -> str:
        """Representación en cadena del objeto Grupo retorno."""
        return (
            f"GrupoRetorno(gr_codigo={self.gr_codigo!r}, us_codigo_lider={self.us_codigo_lider!r})"
        )
