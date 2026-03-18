"""
Repositorio de acceso a datos para Retorno.
Encapsula operaciones de persistencia como creación y consulta,
sin incluir lógica de negocio.
"""
from sqlalchemy.orm import Session
from app.retornos.modelos.retorno_modelo import Retorno
from app.retornos.esquemas.retorno_esquemas import RetornoCreate
import datetime


class RetornoRepository:

    def __init__(self, db: Session):
        self.db = db

    def create(self, data: RetornoCreate) -> Retorno:
        """Crea y persiste un nuevo registro de retorno en la base de datos."""
        retorno = Retorno(
            fecha_creacion=datetime.datetime.now(),
            anio=data.anio,
            estado=data.estado,
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
        return self.db.query(Retorno).filter(Retorno.codigo == codigo).first()
    
    def get_by_fecha(self, fecha: datetime.date) -> Retorno | None:
        """Busca un retorno existente por fecha de creación."""
        return self.db.query(Retorno).filter(Retorno.fecha_creacion == fecha).first()

    def get_by_anio(self, anio: int) -> Retorno | None:
        """Busca un retorno existente por año."""
        return self.db.query(Retorno).filter(Retorno.anio == anio).first()