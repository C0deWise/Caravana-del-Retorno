from sqlalchemy import Column, Integer, String
from app.core.database import Base

class Colonia(Base):
    __tablename__ = "colonia"

    co_codigo = Column(Integer, primary_key = True, index=True, autoincrement=True)
    co_pais = Column(String(100), nullable=False)
    co_departamento = Column(String(100), nullable=False)
    co_ciudad = Column(String(100), nullable=False)
