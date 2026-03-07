from sqlalchemy.orm import Session
from app.colonias.models.colonia_model import Colonia
from app.colonias.schemas.colonia_schemas import ColoniaCreate

def crear_colonia(db: Session, datos: ColoniaCreate) -> Colonia:
    colonia = Colonia(
        pais = datos.pais,
        departamento = datos.departamento,
        ciudad = datos.ciudad,
    )
    db.add(colonia)
    db.commit()
    db.refresh(colonia)
    return colonia

def obtener_colonia_por_ubicacion(db: Session, pais: str, departamento: str, ciudad:str) -> Colonia | None:
    return (
        db.query(Colonia).filter(
            Colonia.pais == pais,
            Colonia.departamento == departamento,
            Colonia.ciudad == ciudad
        ).first()
    )