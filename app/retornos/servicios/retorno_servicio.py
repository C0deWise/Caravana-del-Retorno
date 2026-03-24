"""
Servicio de lógica de negocio para Retorno.
Coordina el repositorio y aplica reglas del dominio,
independiente del framework web.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from app.retornos.repositorios.retorno_repositorio import RetornoRepository
from app.retornos.esquemas.retorno_esquemas import RetornoCreate, RetornoResponse
from app.retornos.excepciones.retorno_excepciones import (
    RetornoNotFoundError,
    RetornoAnioDuplicadoError,
    RetornoAnioPasadoError,
)
import datetime

class RetornoService:

    def __init__(self, db: AsyncSession):
        self.repo = RetornoRepository(db)

    async def crear_retorno(self, data: RetornoCreate) -> RetornoResponse:
        """
        Valida que el año no sea pasado ni esté duplicado,
        luego delega la creación al repositorio.
        """
        # Restricción 1: año no puede ser anterior al actual
        if data.anio < datetime.date.today().year:
            raise RetornoAnioPasadoError()

        # Restricción 2: no puede existir otro retorno con el mismo año
        existente = await self.repo.get_by_anio(data.anio)
        if existente:
            raise RetornoAnioDuplicadoError(data.anio)

        retorno = await self.repo.create(data)
        return RetornoResponse.model_validate(retorno)

    async def listar_retornos(self) -> list[RetornoResponse]:
        """Retorna todos los retornos registrados."""
        retornos = await self.repo.get_all()
        return [RetornoResponse.model_validate(r) for r in retornos]

    async def obtener_retorno(self, codigo: int) -> RetornoResponse:
        """Busca un retorno por código; lanza excepción si no existe."""
        retorno = await self.repo.get_by_codigo(codigo)
        if not retorno:
            raise RetornoNotFoundError(codigo)
        return RetornoResponse.model_validate(retorno)