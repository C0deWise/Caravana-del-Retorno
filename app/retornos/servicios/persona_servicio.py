from fastapi import HTTPException, status
from app.retornos.repositorios.persona_repositorio import PersonaRepositorio
from app.retornos.repositorios.retorno_repositorio import RetornoRepository
from app.retornos.repositorios.grupo_retorno_repositorio import GrupoRetornoRepositorio
from app.retornos.esquemas.persona_esquema import PersonaCrear, PersonaRespuesta
from typing import List

class PersonaServicio:
    def __init__(
        self, 
        repositorio: PersonaRepositorio, 
        repo_retorno: RetornoRepository,
        repo_grupo: GrupoRetornoRepositorio
    ):
        self.repositorio = repositorio
        self.repo_retorno = repo_retorno
        self.repo_grupo = repo_grupo

    async def crear_persona(self, datos: PersonaCrear) -> PersonaRespuesta:
        # Restricción: No duplicados por documento
        if await self.repositorio.obtener_por_documento(datos.pe_documento):
            raise HTTPException(status_code=400, detail="Ya existe una persona con este documento.")
        
        # Restricción: No duplicados por correo
        if datos.pe_correo and await self.repositorio.obtener_por_correo(datos.pe_correo):
            raise HTTPException(status_code=400, detail="Ya existe una persona con este correo.")

        persona = await self.repositorio.crear_persona(datos)
        return PersonaRespuesta.model_validate(persona)

    async def asociar_persona_a_grupo(self, pe_codigo: int, gr_codigo: int):
        # Validar existencia de la persona
        persona = await self.repositorio.obtener_por_id(pe_codigo)
        if not persona:
            raise HTTPException(status_code=404, detail="Persona no encontrada.")

        # Obtener el retorno vigente para aplicar la restricción de "una vez por retorno"
        ultimo_retorno = await self.repo_retorno.obtener_ultimo_retorno()
        if not ultimo_retorno:
            raise HTTPException(status_code=400, detail="No hay un retorno configurado en el sistema.")

        # Verificar si el grupo existe
        grupo = await self.repo_grupo.obtener_grupo_por_id(gr_codigo)
        if not grupo:
            raise HTTPException(
                status_code=404, 
                detail=f"El grupo con código {gr_codigo} no existe."
            )

        # Restricción: Una persona solo puede pertenecer a un Grupo_retorno a la vez por cada retorno
        ya_inscrita = await self.repositorio.persona_ya_en_retorno(pe_codigo, ultimo_retorno.codigo)
        if ya_inscrita:
            raise HTTPException(
                status_code=400, 
                detail="La persona ya pertenece a un grupo en el retorno actual."
            )

        return await self.repositorio.asociar_a_grupo(pe_codigo, gr_codigo)

    async def listar_personas_por_grupo(self, gr_codigo: int) -> List[PersonaRespuesta]:
        personas = await self.repositorio.obtener_personas_por_grupo(gr_codigo)
        return [PersonaRespuesta.model_validate(p) for p in personas]
    
    async def listar_personas(self) -> List[PersonaRespuesta]:
        personas = await self.repositorio.obtener_todas_las_personas()
        return [PersonaRespuesta.model_validate(p) for p in personas]
    
    async def obtener_persona_por_id(self, pe_codigo: int) -> PersonaRespuesta|None:
        persona = await self.repositorio.obtener_por_id(pe_codigo)
        if not persona:
            raise HTTPException(status_code=404, detail="Persona no encontrada.")
        return PersonaRespuesta.model_validate(persona)
    
    async def obtener_persona_por_documento(self, documento: str) -> PersonaRespuesta|None:
        persona = await self.repositorio.obtener_por_documento(documento)
        if not persona:
            raise HTTPException(status_code=404, detail="Persona no encontrada.")
        return PersonaRespuesta.model_validate(persona)
    
    async def verificar_registro_retorno_persona(self, pe_codigo: int, re_codigo: int) -> bool:
        """Verifica si una persona está registrada para un retorno específico."""
        persona_grupo = await self.repositorio.persona_ya_en_retorno(pe_codigo, re_codigo)
        return bool(persona_grupo)


