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

    codigo = Column("co_codigo", Integer, primary_key = True, index=True, autoincrement=True)
    pais = Column("co_pais", String(100), nullable=False)
    departamento = Column("co_departamento", String(100), nullable=True)
    ciudad = Column("co_ciudad", String(100), nullable=True)
    lider = Column("lider_id", Integer, nullable=True)
