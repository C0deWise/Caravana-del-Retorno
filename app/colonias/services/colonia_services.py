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
    
    def servicio_establecer_lider(self, colonia_codigo: int, lider_id: int) -> ColoniaRespuesta:
        """
        Asigna un líder a una colonia existente.
        Parámetros:
            db (Session): Sesión activa de SQLAlchemy.
            colonia_codigo (int): Código de la colonia a actualizar.
            lider_id (int): ID del líder a asignar.
        Retorna:
            ColoniaRespuesta: La colonia actualizada con el nuevo líder.
        Excepciones:
            HTTPException 404: Si la colonia no existe en la base de datos.
        """
        colonia = self.repositorio.obtener_colonia_por_id(colonia_codigo)
        if not colonia:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Colonia con código {colonia_codigo} no encontrada"
            )
        
        usuario_lider
        # TODO: Validar que el líder exista cuando se implemente el módulo de líderes
        colonia_actualizada = self.repositorio.establecer_lider_colonia(colonia_codigo, lider_id)
        return ColoniaRespuesta.model_validate(colonia_actualizada, from_attributes=True)