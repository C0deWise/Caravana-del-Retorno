"""
Modelo para tokens de recuperación de contraseña de un solo uso.
"""

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, UniqueConstraint, func, text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class PasswordRecoveryToken(Base):
    __tablename__ = "password_recovery_token"
    __table_args__ = (
        UniqueConstraint("prt_jti_hash", name="uq_password_recovery_token_jti_hash"),
    )

    prt_codigo: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    us_codigo: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("usuario.us_codigo", ondelete="CASCADE"),
        nullable=False,
    )
    prt_jti_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    prt_created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    prt_expires_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), nullable=False)
    prt_used_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    prt_revocado: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default=text("false"),
    )