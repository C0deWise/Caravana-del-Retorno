"""
Módulo que contiene la lógica de negocio para la entidad Colonia.
Coordina la validación de reglas de negocio y la interacción con el
repositorio de colonias, garantizando la integridad de los datos antes 
de su persistencia en la base de datos.
"""
from sqlalchemy.orm import Session
from app.colonias.schemas.colonia_schemas import ColoniaCrear, ColoniaRespuesta
from app.colonias.repositories.colonia_repository import ColoniaRepository

from fastapi import HTTPException, status


class ColoniaService:

    def __init__(self, repositorio: ColoniaRepository):
        self.repositorio = repositorio

    def servicio_crear_colonia(self, datos: ColoniaCrear) -> ColoniaRespuesta:
        """
        Crear una nueva colonia aplicando reglas de negocio.
        Parámetros:
            db (Session): Sesión activa de SQLAlchemy.
            datos (ColoniaCrear): Datos validados de la colonia a crear.
        Retorna:
            ColoniaRespuesta: Datos de la colonia creada.
        Excepciones:
            HTTPException 409: Si ya existe una colonia con la misma ubicación.
        """
        #Verificar si ya existe una colonia con la misma ubicación.
        colonia_existente = self.repositorio.obtener_colonia_por_ubicacion(
            pais=datos.pais,
            departamento=datos.departamento,
            ciudad=datos.ciudad,
        )

        if colonia_existente and (not datos.departamento or not datos.ciudad): 
            raise HTTPException (
                status_code = status.HTTP_409_CONFLICT,
                detail=f"Ya existe una colonia en {datos.pais}.",
                )
        elif colonia_existente:
            raise HTTPException (
                status_code = status.HTTP_409_CONFLICT,
                detail=f"Ya existe una colonia en {datos.ciudad}, {datos.departamento}, {datos.pais}.",
                )
        
        #Crear la colonia sino existe duplicado
        nueva_colonia = self.repositorio.crear_colonia(datos)
        return ColoniaRespuesta.model_validate(nueva_colonia, from_attributes=True)