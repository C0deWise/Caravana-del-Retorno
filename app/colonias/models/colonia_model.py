from sqlalchemy import Column, Integer, String
from app.core.database import Base

class Colonia(Base):
    __tablename__ = "colonias"

    id = Column(Integer, primary_key = True, index=True, autoincrement=True)
    pais = Column(String(100), nullable=False)
    departamento = Column(String(100), nullable=False)
    ciudad = Column(String(100), nullable=False)
