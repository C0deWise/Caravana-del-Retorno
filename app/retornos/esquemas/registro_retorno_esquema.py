"""
Modulo que define los esquemas para el registro a un retorno.
Contiene los esquemas para estructurar los datos de entrada y salida 
relacionados con el proceso de registro a un retorno.
"""

from typing import Optional

from pydantic import BaseModel, ValidationInfo, field_validator

class RegistroRetornoCrear(BaseModel):
    usuario: int
    retorno: int
    num_hospedaje: int
    num_transporte: int
    num_parqueadero: int
    anotacion: Optional[str] = None

    model_config = {"from_attributes": True}

class RegistroRetornoEditar(BaseModel):
    num_hospedaje: Optional[int] = None
    num_transporte: Optional[int] = None
    num_parqueadero: Optional[int] = None
    anotacion: Optional[str] = None

    @field_validator("num_hospedaje", "num_transporte", "num_parqueadero")
    @classmethod
    def no_negativo(cls, value, info: ValidationInfo):
        if value < 0:
            raise ValueError(f"El campo {info.field_name} no puede ser negativo.")
        return value
    
    @field_validator("num_hospedaje", "num_transporte", "num_parqueadero")
    @classmethod
    def no_mayor_a_uno(cls, value, info: ValidationInfo):
        if value is not None and value > 1:
            raise ValueError(f"El campo {info.field_name} no puede ser mayor a 1.")
        return value

    model_config = {"from_attributes": True}
class RegistroRetornoRespuesta(BaseModel):
    codigo: int
    usuario: int
    retorno: int
    num_hospedaje: int 
    num_transporte: int 
    num_parqueadero: int 
    anotacion: Optional[str] = None

    model_config = {"from_attributes": True}