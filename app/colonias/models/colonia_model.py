"""
Módulo que define el modelo de base de datos para la entidad Colonia.
Representa una colonia colombiana, compuesta por país, departamento y 
ciudad, y una colonia en el exterior compuesta solo por el año. Es 
utilizado por SQLAlchemy para mapear la tabla 'colonias' en PostgreSQL.
"""

from sqlalchemy import Column, Integer, String
from app.core.database import Base

class Colonia(Base):
    """Modelo SQLAlchemy que representa una colonia colombiana."""
    __tablename__ = "colonias"

    co_codigo = Column(Integer, primary_key = True, index=True, autoincrement=True)
    co_pais = Column(String(100), nullable=False)
    co_departamento = Column(String(100), nullable=True)
    co_ciudad = Column(String(100), nullable=True)
    lider_id = Column(Integer, nullable=True)
