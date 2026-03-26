"""
    parentesco_esquemas.py define los esquemas de entrada y salida de Pydantic para las relaciones de parentesco entre usuarios.
"""



from app.usuarios.schemas.usuario_esquemas import UsuarioResumen
from pydantic import BaseModel, field_validator, Field
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

class ParentescoRespuestaDetallada(BaseModel):
    codigo: int = Field(alias="pa_codigo")
    tipo_parentesco: tipoParentesco = Field(alias="pa_tipo_parentesco")
    estado: EstadoSolicitudParentesco = Field(alias="pa_estado")
    solicitante: UsuarioResumen
    destinatario: UsuarioResumen
    model_config = {"from_attributes": True, "populate_by_name": True}