from fastapt import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.colonias.schemas.colonia_schemas import ColoniaCreate, ColoniaResponse
from app.colonias.services.colonia_services import service_crear_colonia

router = APIRouter()

@router.post(
    "/",
    response_model = ColoniaResponse,
    status_code = status.HTTP_201_CREATED,
    summary = "Crear una colonia",
    description = "Crea una nueva colonia con país, departamento y ciudad",
)
def crear_colonia(datos: ColoniaCreate, db: Session = Depends(get_db)):
    return service_crear_colonia(db, datos)