from sqlalchemy import Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime

from app.core.database import Base


class Multimedia(Base):
    __tablename__ = "multimedia"

    codigo: Mapped[int] = mapped_column("mm_codigo", Integer, primary_key=True, autoincrement=True)
    retorno: Mapped[int] = mapped_column("re_codigo", Integer, ForeignKey("retorno.codigo"), nullable=False)
    tipo: Mapped[str] = mapped_column("mm_tipo", String(10), nullable=False)
    url: Mapped[str] = mapped_column("mm_url", String(500), nullable=False)
    nombre_archivo: Mapped[str] = mapped_column("mm_nombre_archivo", String(255), nullable=False)
    fecha_creacion: Mapped[datetime] = mapped_column("mm_fecha_creacion", DateTime, default=datetime.utcnow)