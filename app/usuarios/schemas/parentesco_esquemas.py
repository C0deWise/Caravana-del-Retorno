"""
    parentesco_esquemas.py define los esquemas de entrada y salida de Pydantic para las relaciones de parentesco entre usuarios.
"""



from pydantic import BaseModel, field_validator
from datetime import date
from typing import Optional


from app.usuarios.models.parentesco import EstadoSolicitudParentesco, tipoParentesco

class ParentescoCrear(BaseModel):
    codigo_solicitante: int
    codigo_destinatario: int
    tipo_parentesco: tipoParentesco

class ParentescoRespuesta(BaseModel):
    codigo: int
    fecha_creacion: date
    estado: EstadoSolicitudParentesco
    codigo_solicitante: int
    codigo_destinatario: int
    tipo_parentesco: tipoParentesco

    model_config = {"from_attributes": True}