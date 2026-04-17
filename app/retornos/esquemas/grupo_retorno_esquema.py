


from pydantic import BaseModel
class GrupoRetornoCrear(BaseModel):
    lider: int

    model_config = {"from_attributes": True}
class GrupoRetornoRespuesta(BaseModel):
    codigo: int
    lider: int

    model_config = {"from_attributes": True}