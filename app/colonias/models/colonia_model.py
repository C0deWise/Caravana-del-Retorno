"""
Módulo que define el modelo de base de datos para la entidad Colonia.
Representa una colonia en el exterior, compuesta por país
departamento y ciudad. Es utilizado por SQLAlchemy para mapear la 
tabla 'colonias' en PostgreSQL.
"""

from sqlalchemy import Column, Integer, String
from app.core.database import Base

class Colonia(Base):
    """Modelo SQLAlchemy que representa una colonia colombiana."""
    __tablename__ = "colonias"

    id = Column(Integer, primary_key = True, index=True, autoincrement=True)
    pais = Column(String(100), nullable=False)
    departamento = Column(String(100), nullable=False)
    ciudad = Column(String(100), nullable=False)
