


from datetime import datetime

from pydantic import BaseModel

from app.retornos.esquemas.solicitud_grupo_retorno_esquema import SolicitudGrupoRetornoEstado



class SolicitudRetornoGrupoLiderRespuesta(BaseModel):
    id: int
    usuario_id: int 
    correo_usuario: str
    grupo_id: int 
    estado: SolicitudGrupoRetornoEstado
    timestamp: datetime

class SolicitudRetornoGrupoRespuesta(BaseModel):
    id: int
    usuario_id: int 
    grupo_id: int 
    estado: SolicitudGrupoRetornoEstado
    timestamp: datetime
class SolicitudRetornoGrupoUsuarioRespuesta(BaseModel):
    id: int
    usuario_id: int 
    nombre_lider: str
    grupo_id: int 
    estado: SolicitudGrupoRetornoEstado
    timestamp: datetime