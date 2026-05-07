from datetime import date

from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from app.retornos.modelos.persona_modelo import TipoDoc

class PersonaBase(BaseModel):
    pe_tipo_doc: TipoDoc
    pe_documento: str = Field(..., min_length=5, max_length=20)
    pe_nombre: str = Field(..., min_length=2, max_length=100)
    pe_apellido: str = Field(..., min_length=2, max_length=100)
    pe_correo: Optional[EmailStr] = None
    pe_fecha_nacimiento: date

class PersonaCrear(PersonaBase):
    pass

class PersonaRespuesta(PersonaBase):
    pe_codigo: int

    class Config:
        from_attributes = True

class PersonaGrupoAsociar(BaseModel):
    pe_codigo: int
    gr_codigo: int

class PersonaGrupoRespuesta(BaseModel):
    pgr_codigo: int
    pe_codigo: int
    gr_codigo: int

    class Config:
        from_attributes = True