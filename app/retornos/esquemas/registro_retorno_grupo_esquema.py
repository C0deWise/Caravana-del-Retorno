"""
    registro_retorno_grupo_esquema.py define los esquemas de validación y serialización para el modelo RegistroRetornoGrupo.
"""

from pydantic import BaseModel
from typing import Optional

class RegistroRetornoGrupoCrear(BaseModel):
    retorno: int
    cod_grupo: int
    num_hospedaje: int
    num_transporte: int
    num_parqueadero: int
    anotacion: Optional[str] = None

    model_config = {"from_attributes": True}

class RegistroRetornoGrupoRespuesta(BaseModel):
    regg_codigo: int
    retorno: int
    cod_grupo: int
    num_hospedaje: int
    num_transporte: int
    num_parqueadero: int
    anotacion: Optional[str] = None

    model_config = {"from_attributes": True}
