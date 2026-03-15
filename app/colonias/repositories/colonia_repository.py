"""
Modulo que gestiona el acceso de datos para la entidad Colonia.
Contiene las operaciones de consulta e inserción en la base de datos
relacionadas con colonias colombianas, utilizando sesiones SQLAlchemy
como capa de persistencia.
"""

from sqlalchemy.orm import Session
from app.colonias.models.colonia_model import Colonia
from app.colonias.schemas.colonia_schemas import ColoniaCrear

def crear_colonia(db: Session, datos: ColoniaCrear) -> Colonia:
    """
    Inserta una nueva colonia en la base de datos.
    Parámetros:
        db (Session): Sesión activa de SQLAlchemy.
        datos (ColoniaCrear): Datos validados de la colonia a crear.
    Retorna:
        Colonia: Objeto de la colonia recién creado con su id generado.
    """
    colonia = Colonia(
        pais = datos.pais,
        departamento = datos.departamento,
        ciudad = datos.ciudad,
        lider = datos.lider,
    )
    db.add(colonia)
    db.commit()
    db.refresh(colonia)
    return colonia

def obtener_colonia_por_ubicacion(db: Session, pais: str, departamento: str, ciudad:str) -> Colonia | None:
    """
    Busca una colonia existente por su ubicación exacta.
    Parámetros:
        db (Session): Sesion activa de SQLAlchemy.
        pais (str): País de la colonia.
        departamento (str): Departamento de la colonia.
        ciudad (str): Ciudad de la colonia.
    Retorna:
        Colonia | None: La colonia encontrada o None si no existe.
    """
    return (
        db.query(Colonia).filter(
            Colonia.pais == pais,
            Colonia.departamento == departamento,
            Colonia.ciudad == ciudad
        ).first()
    )