"""
    registro_retorno_grupo_esquema.py define los esquemas de validación y serialización para el modelo RegistroRetornoGrupo.
"""

from pydantic import BaseModel, field_validator, ValidationInfo
from typing import Optional

class RegistroRetornoGrupoCrear(BaseModel):
    retorno: int
    cod_grupo: int
    num_hospedaje: int
    num_transporte: int
    num_parqueadero_carro: int
    num_parqueadero_moto: int
    anotacion: Optional[str] = None

    model_config = {"from_attributes": True}

    @field_validator("num_hospedaje", "num_transporte", "num_parqueadero_carro", "num_parqueadero_moto", "retorno", "cod_grupo")
    @classmethod
    def validar_no_negativo(cls, value, info: ValidationInfo):
        if value < 0:
            raise ValueError(
                f"El campo '{info.field_name}' no puede ser negativo."
            )
        return value

class RegistroRetornoGrupoRespuesta(BaseModel):
    regg_codigo: int
    retorno: int
    cod_grupo: int
    num_hospedaje: int
    num_transporte: int
    num_parqueadero_carro: int
    num_parqueadero_moto: int
    anotacion: Optional[str] = None

    model_config = {"from_attributes": True}

class RegistroRetornoGrupoEditar(BaseModel):
    num_hospedaje: Optional[int] = None
    num_transporte: Optional[int] = None
    num_parqueadero_carro: Optional[int] = None
    num_parqueadero_moto: Optional[int] = None
    anotacion: Optional[str] = None

    model_config = {"from_attributes": True}

    @field_validator("num_hospedaje", "num_transporte", "num_parqueadero_carro", "num_parqueadero_moto")
    @classmethod
    def validar_no_negativo(cls, value, info: ValidationInfo):
        if value is not None and value < 0:
            raise ValueError(f"El campo '{info.field_name}' no puede ser negativo.")
        return value
