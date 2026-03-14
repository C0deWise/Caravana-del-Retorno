from sqlalchemy.orm import Session
from app.colonias.models.colonia_model import Colonia
from app.colonias.schemas.colonia_schemas import ColoniaCreate

def crear_colonia(db: Session, datos: ColoniaCreate) -> Colonia:
    colonia = Colonia(
        co_pais = datos.pais,
        co_departamento = datos.departamento,
        co_ciudad = datos.ciudad,
    )
    db.add(colonia)
    db.commit()
    db.refresh(colonia)
    return colonia

def obtener_colonia_por_ubicacion(db: Session, pais: str, departamento: str, ciudad:str) -> Colonia | None:
    return (
        db.query(Colonia).filter(
            Colonia.co_pais == pais,
            Colonia.co_departamento == departamento,
            Colonia.co_ciudad == ciudad
        ).first()
    )

def obtener_colonias(db: Session) -> list[Colonia]:
    return db.query(Colonia).all()