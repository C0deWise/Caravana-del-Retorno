"""
Servicio de lógica de negocio para Retorno.
Coordina el repositorio y aplica reglas del dominio,
independiente del framework web.
"""

from sqlalchemy.orm import Session
from app.retornos.repositories.retorno_repository import RetornoRepository
from app.retornos.schemas.retorno_schemas import RetornoCreate, RetornoResponse
from app.retornos.exceptions.retorno_exceptions import (
    RetornoNotFoundError,
    RetornoAnioDuplicadoError,
    RetornoAnioPasadoError,
)
import datetime

class RetornoService:

    def __init__(self, db: Session):
        self.repo = RetornoRepository(db)

    def crear_retorno(self, data: RetornoCreate) -> RetornoResponse:
        """
        Valida que el año no sea pasado ni esté duplicado,
        luego delega la creación al repositorio.
        """
        # Restricción 1: año no puede ser anterior al actual
        if data.re_anio < datetime.date.today().year:
            raise RetornoAnioPasadoError()

        # Restricción 2: no puede existir otro retorno con el mismo año
        existente = self.repo.get_by_anio(data.re_anio)
        if existente:
            raise RetornoAnioDuplicadoError(data.re_anio)

        retorno = self.repo.create(data)
        return RetornoResponse.model_validate(retorno)

    def listar_retornos(self) -> list[RetornoResponse]:
        """Retorna todos los retornos registrados."""
        return [RetornoResponse.model_validate(r) for r in self.repo.get_all()]

    def obtener_retorno(self, codigo: int) -> RetornoResponse:
        """Busca un retorno por código; lanza excepción si no existe."""
        retorno = self.repo.get_by_codigo(codigo)
        if not retorno:
            raise RetornoNotFoundError(codigo)
        return RetornoResponse.model_validate(retorno)