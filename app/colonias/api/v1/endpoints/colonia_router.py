from fastapt import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.colonias.schemas.colonia_schemas import ColoniaCreate, ColoniaResponse
from app.colonias.schemas.colonia_solicitud_schemas import SolicitudColoniaCrear
from app.colonias.services.colonia_services import service_crear_colonia
from app.colonias.services.solicitud_colonis_services import SolicitudColoniaService
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


@router.post(
    "/",
    response_model = ColoniaResponse,
    status_code = status.HTTP_201_CREATED,
    summary = "Crear una solicitud de ingreso a una colonia",
    description = "Crea una nueva solicitud de ingreso a una colonia con el código de usuario y el código de colonia",
)
def crear_solicitud_colonia(datos: SolicitudColoniaCrear, db: Session = Depends(get_db)):
    return SolicitudColoniaService().crear_solicitud(db, datos)
