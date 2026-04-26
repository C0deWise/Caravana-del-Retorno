from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import date
from app.retornos.modelos.persona_modelo import TipoDoc

class PersonaCrear(BaseModel):
    tipo_doc: TipoDoc
    documento: str
    nombre: str
    apellido: str
    correo: Optional[EmailStr] = None
    fecha_nacimiento: date
    cod_registro_grupo: int = Field(..., description="ID del registro del grupo en el retorno (regg_codigo)")

class PersonaRespuesta(BaseModel):
    pe_codigo: int
    pe_tipo_doc: TipoDoc
    pe_documento: str
    pe_nombre: str
    pe_apellido: str
    pe_correo: Optional[str]
    pe_fecha_nacimiento: str
    regg_codigo: int
    model_config = {"from_attributes": True}
