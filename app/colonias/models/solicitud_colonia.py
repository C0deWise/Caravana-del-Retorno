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

    codigo = Column("so_codigo", Integer, primary_key=True, index=True, autoincrement=True)
    usuario_id = Column("us_codigo", Integer, ForeignKey("usuario.us_codigo"), nullable=False)
    colonia_id = Column("co_codigo", Integer, ForeignKey("colonia.co_codigo"), nullable=False)
    estado = Column(
        "so_estado",
        Enum(EstadoSolicitud),
        nullable=False,
        default=EstadoSolicitud.pendiente,
    )
    fecha_creacion = Column("so_fecha_creacion", DateTime, nullable=False, default=datetime.utcnow)

    # Relaciones (opcionales, ajusta según tus modelos)
    usuario = relationship("Usuario")
    colonia = relationship("Colonia")