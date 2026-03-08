"""
Modelo ORM para la entidad Retorno.
Representa la tabla 'retorno' con su clave primaria,
fecha de creación, año y estado del retorno.
"""

from sqlalchemy import Column, Integer, Date, String, UniqueConstraint
from app.core.database import Base
import datetime


class Retorno(Base):
    __tablename__ = "retorno"

    re_codigo = Column(Integer, primary_key=True, index=True, autoincrement=True)
    re_fecha_creacion = Column(Date, nullable=False, default=datetime.date.today)
    re_año = Column(Integer, nullable=False)
    re_estado = Column(String(50), nullable=False, default="activo")

    __table_args__ = (
        UniqueConstraint("re_fecha_creacion", name="uk1_retorno"),
        UniqueConstraint("re_año", name="uk2_retorno"),
    )