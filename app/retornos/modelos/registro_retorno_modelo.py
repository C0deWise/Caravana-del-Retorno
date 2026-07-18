"""
Modulo que define el modelo para el registro a un retorno.
Aquí se mapea la tabla de registro a un retorno en la base de datos, definiendo 
sus columnas y relaciones.
"""

from sqlalchemy import Integer, Boolean, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base

class RegistroRetorno(Base):
    __tablename__ = 'registro_retorno'

    codigo: Mapped[int] = mapped_column("reg_codigo",Integer, primary_key=True, autoincrement=True)
    usuario: Mapped[int] = mapped_column("us_codigo", Integer, ForeignKey("usuario.us_codigo"), nullable=False)
    retorno: Mapped[int] = mapped_column("re_codigo", Integer, ForeignKey("retorno.codigo"), nullable=False)
    num_hospedaje: Mapped[int] = mapped_column("reg_num_hospedaje", Integer, nullable=False, default=0)
    num_transporte: Mapped[int] = mapped_column("reg_num_transporte", Integer, nullable=False, default=0)
    num_parqueadero_carro: Mapped[int] = mapped_column("reg_num_parqueadero_carro", Integer, nullable=False, default=0)
    num_parqueadero_moto: Mapped[int] = mapped_column("reg_num_parqueadero_moto", Integer, nullable=False, default=0)

    anotacion: Mapped[str] = mapped_column("reg_anotacion", String(500), nullable=True)

    __table_args__ = (
        UniqueConstraint("us_codigo", "re_codigo", name="uk1_uk2_registro_retorno"),
    )