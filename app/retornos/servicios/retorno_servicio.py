"""
Servicio de lógica de negocio para Retorno.
Coordina el repositorio y aplica reglas del dominio,
independiente del framework web.
"""

from app.retornos.servicios.retorno_maquina_estados import RetornoEstadoTransicion
from sqlalchemy.ext.asyncio import AsyncSession
from app.retornos.repositorios.retorno_repositorio import RetornoRepository
from app.retornos.esquemas.retorno_esquemas import RetornoCreate, RetornoEstado, RetornoResponse
from app.retornos.excepciones.retorno_excepciones import (
    RetornoEstadoEnCursoaActivoError,
    RetornoEstadoFinalizadoError,
    RetornoEstadoActivoaFinalizadoError,
    RetornoNotFoundError,
    RetornoAnioDuplicadoError,
    RetornoAnioPasadoError,
    RetornoVigenteError,
    NoHayRetornoVigenteError
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

        # Restricción 3: solo puede haber un retorno activo o en curso a la vez
        retornos_vigentes = await self.repo.obtener_retorno_por_estado(RetornoEstado.ACTIVO) + await self.repo.obtener_retorno_por_estado(RetornoEstado.EN_CURSO)
        if data.estado != RetornoEstado.FINALIZADO and retornos_vigentes:
            raise RetornoVigenteError()
        
        retorno = await self.repo.create(data)
        return RetornoResponse.model_validate(retorno)

    async def obtener_retorno_vigente(self) -> RetornoResponse | None:
        """Obtiene el retorno vigente, si existe alguno."""
        retornos_activos = await self.repo.obtener_retorno_por_estado(RetornoEstado.ACTIVO)
        if retornos_activos:
            return RetornoResponse.model_validate(retornos_activos[0])
        
        retornos_en_curso = await self.repo.obtener_retorno_por_estado(RetornoEstado.EN_CURSO)
        if retornos_en_curso:
            return RetornoResponse.model_validate(retornos_en_curso[0])
        
        raise  NoHayRetornoVigenteError()
    async def obtener_ultimo_retorno(self) -> RetornoResponse | None:
        """Obtiene el retorno con el año más reciente."""
        retorno = await self.repo.obtener_ultimo_retorno()
        if retorno:
            return RetornoResponse.model_validate(retorno)
        return None
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
    
    async def cambiar_estado_retorno(self, codigo: int, nuevo_estado: RetornoEstado) -> RetornoResponse:
        """Actualiza el estado de un retorno existente."""

        retorno = await self.repo.get_by_codigo(codigo)
        if not retorno:
            raise RetornoNotFoundError(codigo)
        RetornoEstadoTransicion.validar_transicion(retorno.estado, nuevo_estado)
        retorno_actualizado = await self.repo.cambiar_estado_retorno(codigo, nuevo_estado)
        return RetornoResponse.model_validate(retorno_actualizado)