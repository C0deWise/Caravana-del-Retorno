"""
Modulo que define los esquemas para el registro a un retorno.
Contiene los esquemas para estructurar los datos de entrada y salida 
relacionados con el proceso de registro a un retorno.
"""

from pydantic import BaseModel

class RegistroRetornoCrear(BaseModel):
    usuario: int
    retorno: int
    num_hospedaje: int
    num_transporte: int
    num_parqueadero: int

    model_config = {"from_attributes": True}

class RegistroRetornoRespuesta(BaseModel):
    codigo: int
    usuario: int
    retorno: int
    num_hospedaje: int 
    num_transporte: int 
    num_parqueadero: int 

    model_config = {"from_attributes": True}