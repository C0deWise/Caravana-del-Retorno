



from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated
from app.core.database import get_db
from app.reportes.repositories.colonia_reporte_repositorio import ColoniaReporteRepositorio
from app.reportes.repositories.grupo_retorno_reporte_repositorio import GrupoReportoReporteRepositorio
from app.reportes.repositories.persona_reporte_repositorio import PersonaReporteRepositorio
from app.reportes.repositories.usuario_retorno_reporte_repositorio import UsuarioRetornoReporteRepositorio
from app.reportes.services.reportes_service import ReportesService

def get_reportes_servicio(db: Annotated[AsyncSession, Depends(get_db)]) -> ReportesService:
    repositorio_reportes_colonia = ColoniaReporteRepositorio(db)
    repositorio_reportes_persona = PersonaReporteRepositorio(db)
    repositorio_reportes_usuario = UsuarioRetornoReporteRepositorio(db)
    repositorio_reportes_grupo =  GrupoReportoReporteRepositorio(db)
    return ReportesService(repositorio_colonia =  repositorio_reportes_colonia, 
                           repositorio_usuario = repositorio_reportes_usuario, repositorio_grupo = repositorio_reportes_grupo, 
                           repositorio_persona = repositorio_reportes_persona)


router = APIRouter(prefix="/reportes", tags=["Reportes"])


@router.get("/reporte-asistencia-colonia/{retorno_id}/{colonia_id}",
            status_code = status.HTTP_200_OK,
            summary = "Generar el informe de asistencia de una colonia a un retorno",
            )
async def generar_reporte_asistencia_colonia(retorno_id:int, colonia_id:int, servicio: Annotated[ReportesService, Depends(get_reportes_servicio)]):
    reporte_pdf = await servicio.generar_reporte_asistencia_retorno_colonia(colonia_id, retorno_id)
    return reporte_pdf


@router.get("/reporte-general-asistencia/{retorno_id}",
            status_code = status.HTTP_200_OK,
            summary = "Generar el informe de asistencia general de un retorno",
            )
async def generar_reporte_asistencia_general(retorno_id:int, servicio: Annotated[ReportesService, Depends(get_reportes_servicio)]):
    reporte_pdf = await servicio.generar_reporte_general_retorno(retorno_id)
    return reporte_pdf
