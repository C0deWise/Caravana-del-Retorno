"""
Endpoints HTTP para el módulo Retorno.
Expone operaciones de creación y consulta bajo el prefijo /retornos,
con documentación Swagger integrada.
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.retornos.esquemas.retorno_esquemas import RetornoCreate, RetornoResponse
from app.retornos.servicios.retorno_servicio import RetornoService

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
        "Crea un nuevo registro de retorno. "
        "El año no puede ser anterior al actual ni estar ya asociado a otro retorno."
    ),
    responses={
        409: {
            "description": "Ya existe un evento de El Retorno para el año seleccionado.",
            "content": {"application/json": {"example": {"detail": "Ya existe un evento de El Retorno para el año seleccionado: 2024."}}},
        },
        422: {
            "description": "Año anterior al año actual del sistema.",
            "content": {"application/json": {"example": {"detail": "No es posible crear un evento de El Retorno en un año anterior al actual."}}},
        },
    },
)
def crear_retorno(data: RetornoCreate, db: Session = Depends(get_db)):
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