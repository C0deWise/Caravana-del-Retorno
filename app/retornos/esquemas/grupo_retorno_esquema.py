"""
    grupo_retorno_esquema.py define los esquemas de validación para la creación y respuesta de grupos de retorno.
"""


from pydantic import BaseModel
class GrupoRetornoCrear(BaseModel):
    lider: int

    model_config = {"from_attributes": True}
class GrupoRetornoRespuesta(BaseModel):
    codigo: int
    lider: int

    model_config = {"from_attributes": True}