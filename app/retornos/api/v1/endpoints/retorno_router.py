"""
Endpoints HTTP para el módulo Retorno.
Expone operaciones de creación y consulta bajo el prefijo /retornos,
con documentación Swagger integrada.
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.retornos.schemas.retorno_schemas import RetornoCreate, RetornoResponse
from app.retornos.services.retorno_service import RetornoService

router = APIRouter(
    prefix="/retornos",
    tags=["Retornos"],
)


@router.post(
    "/",
    response_model=RetornoResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un nuevo retorno",
    description=(
        "Crea un nuevo registro de retorno con el año y estado especificados. "
        "La fecha de creación se asigna automáticamente al momento de la operación."
    ),
)
def crear_retorno(
    data: RetornoCreate,
    db: Session = Depends(get_db),
):
    service = RetornoService(db)
    return service.crear_retorno(data)


@router.get(
    "/",
    response_model=list[RetornoResponse],
    summary="Listar todos los retornos",
    description="Obtiene el listado completo de retornos registrados en el sistema.",
)
def listar_retornos(db: Session = Depends(get_db)):
    service = RetornoService(db)
    return service.listar_retornos()


@router.get(
    "/{codigo}",
    response_model=RetornoResponse,
    summary="Obtener retorno por código",
    description="Busca y retorna un retorno específico usando su código primario. Retorna 404 si no existe.",
)
def obtener_retorno(codigo: int, db: Session = Depends(get_db)):
    service = RetornoService(db)
    return service.obtener_retorno(codigo)