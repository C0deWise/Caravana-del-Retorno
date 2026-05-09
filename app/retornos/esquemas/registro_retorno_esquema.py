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
    num_parqueadero_carro: int
    num_parqueadero_moto: int
    anotacion: Optional[str] = None

    model_config = {"from_attributes": True}

    @field_validator("num_hospedaje", "num_transporte", "num_parqueadero_carro", "num_parqueadero_moto", "retorno", "usuario")
    @classmethod
    def validar_no_negativo(cls, value, info: ValidationInfo):
        if value < 0:
            raise ValueError(f"El campo '{info.field_name}' no pueden ser negativos.")
        return value
    
    @field_validator("num_hospedaje", "num_transporte", "num_parqueadero_carro", "num_parqueadero_moto")
    @classmethod
    def validar_no_mayor_uno(cls, value, info: ValidationInfo):
        if value > 1:
            raise ValueError(f"El campo '{info.field_name}' no puede ser mayor a 1.")
        return value

class RegistroRetornoRespuesta(BaseModel):
    codigo: int
    usuario: int
    retorno: int
    num_hospedaje: int 
    num_transporte: int 
    num_parqueadero_carro: int 
    num_parqueadero_moto: int 
    anotacion: Optional[str] = None

    model_config = {"from_attributes": True}

class RegistroRetornoDarseDeBaja(BaseModel):
    usuario: int
    retorno: int

    model_config = {"from_attributes": True}

class RegistroRetornoDarseDeBajaRespuesta(BaseModel):
    mensaje: str
    model_config = {"from_attributes": True}

