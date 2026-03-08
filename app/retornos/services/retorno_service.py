"""
Servicio de lógica de negocio para Retorno.
Coordina el repositorio y aplica reglas del dominio,
independiente del framework web.
"""

from sqlalchemy.orm import Session
from app.retornos.repositories.retorno_repository import RetornoRepository
from app.retornos.schemas.retorno_schemas import RetornoCreate, RetornoResponse
from app.retornos.exceptions.retorno_exceptions import RetornoNotFoundError


class RetornoService:

    def __init__(self, db: Session):
        self.repo = RetornoRepository(db)

    def crear_retorno(self, data: RetornoCreate) -> RetornoResponse:
        """Aplica reglas de negocio y delega la creación al repositorio."""
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