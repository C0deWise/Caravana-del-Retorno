from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Colonia(Base):
    __tablename__ = "colonia"

    co_codigo: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    co_pais: Mapped[str] = mapped_column(String, nullable=False)
    co_departamento: Mapped[str | None] = mapped_column(String, nullable=True)
    co_ciudad: Mapped[str | None] = mapped_column(String, nullable=True)
    lider: Mapped[int | None] = mapped_column(Integer, nullable=True)

    def __repr__(self) -> str:
        return (
            f"Colonia(id={self.co_codigo!r}, co_pais={self.co_pais!r}, "
            f"co_departamento={self.co_departamento!r}, co_ciudad={self.co_ciudad!r})"
            f"lider={self.lider!r}"
        )
