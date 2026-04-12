
from pydantic import BaseModel, Field
import datetime

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