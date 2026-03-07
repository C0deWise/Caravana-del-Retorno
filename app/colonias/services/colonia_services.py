from sqlalchemy.orm import Session
from app.colonias.schemas.colonia_schemas import ColoniaCreate, ColoniaResponse
from app.colonias.repositories.colonia_repository import (crear_colonia, obtener_colonia_por_ubicacion,)
from fastapi import HTTPException, status

def service_crear_colonia(db: Session, datos: ColoniaCreate) -> ColoniaResponse:
    colonia_existente = obtener_colonia_por_ubicacion(
        db,
        pais=datos.pais,
        departamento=datos.departamento,
        ciudad=datos.ciudad,
    )

    if colonia_existente: 
        raise HTTPException (
            status_code = status.HTTP_409_CONFLICT,
            detail=f"Ya existe una colonia en {datos.ciudad}, {datos.departamento}, {datos.pais}.",
            )
    
    nueva_colonia = crear_colonia(db, datos)
    return ColoniaResponse.model_validate(nueva_colonia)