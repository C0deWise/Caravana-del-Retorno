"""
Modelo ORM para la entidad Retorno.
Representa la tabla 'retorno' con su clave primaria,
fecha de creación, año y estado del retorno.
"""

from sqlalchemy import Integer, DateTime, Enum, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base
from app.retornos.esquemas.retorno_esquemas import RetornoEstado
import datetime


class Retorno(Base):
    __tablename__ = "retorno"

    codigo: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    fecha_creacion: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, default=datetime.datetime.now)
    anio: Mapped[int] = mapped_column(Integer, nullable=False)
    estado: Mapped[RetornoEstado] = mapped_column(Enum(RetornoEstado), nullable=False, default=RetornoEstado.ACTIVO)

    __table_args__ = (
        UniqueConstraint("anio", name="uk2_retorno"),
    )