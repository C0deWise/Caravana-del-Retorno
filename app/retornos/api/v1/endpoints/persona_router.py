from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.retornos.esquemas.persona_esquema import PersonaCrear, PersonaRespuesta, PersonaGrupoAsociar, PersonaGrupoRespuesta
from app.retornos.repositorios.persona_repositorio import PersonaRepositorio
from app.retornos.repositorios.retorno_repositorio import RetornoRepository
from app.retornos.repositorios.grupo_retorno_repositorio import GrupoRetornoRepositorio
from app.retornos.repositorios.registro_retorno_grupo_repositorio import RegistroRetornoGrupoRepositorio
from app.retornos.servicios.persona_servicio import PersonaServicio
from typing import List, Annotated

router = APIRouter(prefix="/personas", tags=["Personas (Asistentes No Usuarios)"])

def get_persona_servicio(db: Annotated[AsyncSession, Depends(get_db)]):
    repo = PersonaRepositorio(db)
    repo_retorno = RetornoRepository(db)
    repo_grupo = GrupoRetornoRepositorio(db) # Correctly instantiate GrupoRetornoRepositorio
    return PersonaServicio(repo, repo_retorno, repo_grupo) # Pass the correct repository

@router.post("/", response_model=PersonaRespuesta, status_code=status.HTTP_201_CREATED)
async def crear_persona(datos: PersonaCrear, servicio: Annotated[PersonaServicio, Depends(get_persona_servicio)]):
    """Crea una persona que asistirá a un retorno."""
    return await servicio.crear_persona(datos)

@router.post("/asociar-grupo", response_model=PersonaGrupoRespuesta, status_code=status.HTTP_201_CREATED)
async def asociar_persona_a_grupo(
    datos: PersonaGrupoAsociar, 
    servicio: Annotated[PersonaServicio, Depends(get_persona_servicio)]
):
    """Relaciona una persona con un grupo de retorno."""
    return await servicio.asociar_persona_a_grupo(datos.pe_codigo, datos.gr_codigo)

@router.get("/grupo/{gr_codigo}", response_model=List[PersonaRespuesta])
async def obtener_personas_de_grupo(
    gr_codigo: int, 
    servicio: Annotated[PersonaServicio, Depends(get_persona_servicio)]
):
    """Lista todas las personas que pertenecen a un grupo específico."""
    return await servicio.listar_personas_por_grupo(gr_codigo)

@router.get("/{pe_codigo}", response_model=PersonaRespuesta)
async def obtener_persona_por_id(pe_codigo:int, servicio: Annotated[PersonaServicio, Depends(get_persona_servicio)]):
    """Obtiene los detalles de una persona por su código."""
    persona = await servicio.repositorio.obtener_por_id(pe_codigo)
    if not persona:
        return None
    return PersonaRespuesta.model_validate(persona)

@router.get("/documento/{documento}", response_model=PersonaRespuesta)
async def obtener_persona_por_documento(documento:str, servicio: Annotated[PersonaServicio, Depends(get_persona_servicio)]):
    persona = await servicio.repositorio.obtener_persona_por_documento(documento)
    if not persona:
        return None
    return PersonaRespuesta.model_validate(persona)


@router.get("/",response_model=List[PersonaRespuesta])
async def listar_personas(servicio: Annotated[PersonaServicio, Depends(get_persona_servicio)]):
    """Lista todas las personas registradas en el sistema."""
    return await servicio.repositorio.obtener_todas_las_personas()
