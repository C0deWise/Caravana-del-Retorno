from pydantic import BaseModel, field_validator
import re

class ColoniaCreate (BaseModel):
    pais: str
    departamento: str
    ciudad: str

    @field_validator("pais", "departamento", "ciudad")
    @classmethod
    def solo_alfabetico(cls, v:str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("El campo no puede estar vacío")
        if not re.match(r"^[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ\s\-]+$", v):
            raise ValueError("El campo solo puede contener letras.")
        return v
    
class ColoniaResponse (BaseModel):
    id: int
    pais: str
    departamento: str
    ciudad: str

    model_config = {"from_attributes": True}