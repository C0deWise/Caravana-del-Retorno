"""
    grupo_retorno_servicio.py define el servicio para gestionar los grupos de retornos, solicitudes a grupos de retorno,
    y la asociación de usuarios a grupos de retorno. 
"""

from app.retornos.repositorios.grupo_retorno_repositorio import GrupoRetornoRepositorio
from app.retornos.repositorios.retorno_grupo_usuario_repositorio import RetornoGrupoUsuarioRepositorio
from app.retornos.repositorios.retorno_repositorio import RetornoRepository
from app.retornos.repositorios.solicitud_grupo_retorno_repositorio import SolicitudGrupoRetornoRepositorio
from app.usuarios.repository.usuario_repositorio import UsuarioRepositorio


class GrupoRetornoServicio:
    def __init__(self, repositorio_retorno: RetornoRepository, repositorio_grupos: GrupoRetornoRepositorio, repositorio_solicitudes: SolicitudGrupoRetornoRepositorio , repositorio_usuario_grupo: RetornoGrupoUsuarioRepositorio, repositorio_usuario: UsuarioRepositorio = None):
        self.repositorio_retorno = repositorio_retorno
        self.repositorio_grupos = repositorio_grupos
        self.repositorio_solicitudes = repositorio_solicitudes
        self.repositorio_usuario_grupo = repositorio_usuario_grupo
        self.repositorio_usuario = repositorio_usuario

    async def crear_grupo_retorno(self, datos):
        pass
    
    async def existe_grupo_retorno(self, gr_codigo_int) -> bool:
        pass
    async def crear_solicitud_grupo_retorno(self, datos):
        pass
    
    async def aceptar_solicitud_grupo_retorno(self, datos):
        pass

    async def rechazar_solicitud_grupo_retorno(self, datos):
        pass

    async def _asociar_usuario_a_grupo_retorno(self, datos):
        pass