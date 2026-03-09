"""
Modelo ORM para la entidad Retorno.
Representa la tabla 'retorno' con su clave primaria,
fecha de creación, año y estado del retorno.
"""

from sqlalchemy import Column, Integer, DateTime, String, UniqueConstraint
from app.core.database import Base
import datetime


class Retorno(Base):
    __tablename__ = "retorno"

    re_codigo = Column(Integer, primary_key=True, index=True, autoincrement=True)
    re_fecha_creacion = Column(DateTime, nullable=False, default=datetime.datetime.now)
    re_anio = Column(Integer, nullable=False)
    re_estado = Column(String(50), nullable=False, default="activo")

    __table_args__ = (
        UniqueConstraint("re_anio", name="uk2_retorno"),
    )