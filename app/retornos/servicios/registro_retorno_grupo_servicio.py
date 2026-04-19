"""
    registro_retorno_grupo_servicio.py define el servicio para gestionar el registro de grupos a retornos.
"""




from app.retornos.repositorios.persona_repositorio import PersonaRepositorio
from app.retornos.repositorios.registro_retorno_grupo_repositorio import RegistroRetornoGrupoRepositorio


class RegistroRetornoGrupoServicio: 
    def __init__(self, repositorio_registro_grupo: RegistroRetornoGrupoRepositorio, persona_repositorio: PersonaRepositorio):
        self.repositorio_registro_grupo = repositorio_registro_grupo
        self.persona_repositorio = persona_repositorio

    async def crear_registro_retorno_grupo(self, datos):
        pass

    async def crear_persona(self, datos):
        pass

    
