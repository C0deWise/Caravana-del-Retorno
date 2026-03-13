import enum
from datetime import datetime

from sqlalchemy import Column, Integer, ForeignKey, Enum, DateTime
from sqlalchemy.orm import relationship

from app.core.database import Base  # ajusta este import según tu proyecto


class EstadoSolicitud(str, enum.Enum):
    pendiente = "pendiente"
    aceptada = "aceptada"
    rechazada = "rechazada"
    expirada = "expirada"

class SolicitudColonia(Base):
    __tablename__ = "solicitud_colonia"

    so_codigo = Column(Integer, primary_key=True, index=True, autoincrement=True)
    us_codigo = Column(Integer, ForeignKey("usuario.us_codigo"), nullable=False)
    co_codigo = Column(Integer, ForeignKey("colonia.co_codigo"), nullable=False)
    so_estado = Column(
        Enum(EstadoSolicitud),
        nullable=False,
        default=EstadoSolicitud.pendiente,
    )
    so_fecha_creacion = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relaciones (opcionales, ajusta según tus modelos)
    usuario = relationship("Usuario", back_populates="solicitudes_colonia")
    colonia = relationship("Colonia", back_populates="solicitudes")