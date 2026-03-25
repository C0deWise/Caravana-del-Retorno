"""
Modulo que gestiona el acceso de datos para la entidad Colonia.
Contiene las operaciones de consulta e inserción en la base de datos
relacionadas con colonias colombianas, utilizando sesiones SQLAlchemy
como capa de persistencia.
"""

from sqlalchemy.orm import Session
from app.colonias.models.colonia_model import Colonia
from app.colonias.schemas.colonia_schemas import ColoniaCrear

class ColoniaRepository:
    
    def __init__(self, db: Session):
        self.db = db

    def crear_colonia(self, datos: ColoniaCrear) -> Colonia:
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
        self.db.add(colonia)
        self.db.commit()
        self.db.refresh(colonia)
        return colonia

    def obtener_colonia_por_ubicacion(self, pais: str, departamento: str, ciudad:str) -> Colonia | None:
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
            self.db.query(Colonia).filter(
                Colonia.pais == pais,
                Colonia.departamento == departamento,
                Colonia.ciudad == ciudad
            ).first()
        )
    
    def obtener_colonia_por_id(self, colonia_codigo: int) -> Colonia | None:
        """
        Busca una colonia por su ID.
        Parámetros:
            db (Session): Sesión activa de SQLAlchemy.
            colonia_codigo (int): Código de la colonia a buscar.
        Retorna:
            Colonia | None: La colonia encontrada o None si no existe.
        """
        return self.db.query(Colonia).filter(Colonia.codigo == colonia_codigo).first()

    def establecer_lider_colonia(self, colonia_codigo: int, lider_id: int) -> Colonia:
        """
        Asigna un líder a una colonia existente.
        Parámetros:
            db (Session): Sesión activa de SQLAlchemy.
            colonia_codigo (int): Código de la colonia a actualizar.
            lider_id (int): ID del líder a asignar.
        Retorna:
            Colonia: La colonia actualizada con el nuevo líder.
        """
        colonia = self.obtener_colonia_por_id(colonia_codigo)
        
        colonia.lider = lider_id
        self.db.commit()
        self.db.refresh(colonia)
        return colonia
