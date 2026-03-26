"""
Modelo ORM para la entidad Retorno.
Representa la tabla 'retorno' con su clave primaria,
fecha de creación, año y estado del retorno.
"""

from sqlalchemy import Column, Integer, DateTime, Enum, UniqueConstraint
from app.core.database import Base
from app.retornos.esquemas.retorno_esquemas import RetornoEstado
import datetime


class Retorno(Base):
    __tablename__ = "retorno"

    codigo = Column(Integer, primary_key=True, index=True, autoincrement=True)
    fecha_creacion = Column(DateTime, nullable=False, default=datetime.datetime.now)
    anio = Column(Integer, nullable=False)
    estado = Column(Enum(RetornoEstado), nullable=False, default=RetornoEstado.ACTIVO)

    __table_args__ = (
        UniqueConstraint("anio", name="uk2_retorno"),
    )