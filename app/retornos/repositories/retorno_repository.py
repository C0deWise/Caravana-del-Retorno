"""
Repositorio de acceso a datos para Retorno.
Encapsula operaciones de persistencia como creación y consulta,
sin incluir lógica de negocio.
"""

from sqlalchemy.orm import Session
from app.retornos.models.retorno_model import Retorno
from app.retornos.schemas.retorno_schemas import RetornoCreate
import datetime


class RetornoRepository:

    def __init__(self, db: Session):
        self.db = db

    def create(self, data: RetornoCreate) -> Retorno:
        """Crea y persiste un nuevo registro de retorno en la base de datos."""
        retorno = Retorno(
            re_fecha_creacion=datetime.date.today(),
            re_año=data.re_año,
            re_estado=data.re_estado,
        )
        self.db.add(retorno)
        self.db.commit()
        self.db.refresh(retorno)
        return retorno

    def get_all(self) -> list[Retorno]:
        """Obtiene todos los registros de retorno."""
        return self.db.query(Retorno).all()

    def get_by_codigo(self, codigo: int) -> Retorno | None:
        """Obtiene un retorno por su código primario."""
        return self.db.query(Retorno).filter(Retorno.re_codigo == codigo).first()