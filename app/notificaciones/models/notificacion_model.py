




import enum

from sqlalchemy import DateTime, ForeignKey, Integer, String, func, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

class NotificacionEstado(str, enum.Enum):
    SIN_LEER = "sin_leer"
    LEIDA = "leida"

class Evento(Base):
    __tablename__ = "evento"
    ev_codigo: Mapped[int] = mapped_column("ev_codigo", Integer, primary_key=True, autoincrement=True)
    ev_nombre: Mapped[str] = mapped_column("ev_nombre", String, nullable=False, unique=True)
    ev_descripcion: Mapped[str] = mapped_column("ev_descripcion", String)

class Notificacion(Base):
    __tablename__ = "notificacion"
    no_codigo: Mapped[int] = mapped_column("no_codigo", Integer, primary_key=True, autoincrement=True)
    no_mensaje: Mapped[str] = mapped_column("no_mensaje", String)
    us_codigo_receptor: Mapped[int] = mapped_column("us_codigo_receptor", Integer, ForeignKey("usuario.us_codigo"), nullable=False)
    no_time_stamp: Mapped[DateTime] = mapped_column(
        "no_time_stamp",
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    no_estado: Mapped[NotificacionEstado] = mapped_column("no_estado", Enum(NotificacionEstado), nullable=False, default= NotificacionEstado.SIN_LEER)
    ev_codigo: Mapped[int] = mapped_column("ev_codigo", Integer, ForeignKey("evento.ev_codigo"), nullable=False)
    evento: Mapped[Evento] = relationship("Evento")