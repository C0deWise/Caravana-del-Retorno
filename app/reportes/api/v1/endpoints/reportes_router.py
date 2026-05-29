
"""
reportes_router.py
=================
Propósito: Define los endpoints (rutas) de la API para generar reportes de retornos.
          Incluye endpoints para generar reportes de asistencia por colonia
          y reportes generales de retornos.
"""

from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated
from app.core.database import get_db
from app.reportes.repositories.colonia_reporte_repositorio import ColoniaReporteRepositorio
from app.reportes.repositories.grupo_retorno_reporte_repositorio import GrupoReportoReporteRepositorio
from app.reportes.repositories.persona_reporte_repositorio import PersonaReporteRepositorio
from app.reportes.repositories.usuario_retorno_reporte_repositorio import UsuarioRetornoReporteRepositorio
from app.reportes.services.reportes_service import ReportesService
from app.retornos.repositorios.registro_retorno_grupo_repositorio import RegistroRetornoGrupoRepositorio
from app.retornos.repositorios.registro_retorno_repositorio import RegistroRetornoRepositorio
from app.usuarios.auth_dependencies import require_roles
from app.usuarios.models.usuario import Usuario

def get_reportes_servicio(db: Annotated[AsyncSession, Depends(get_db)]) -> ReportesService:
    repositorio_reportes_colonia = ColoniaReporteRepositorio(db)
    repositorio_reportes_persona = PersonaReporteRepositorio(db)
    repositorio_reportes_usuario = UsuarioRetornoReporteRepositorio(db)
    repositorio_reportes_grupo =  GrupoReportoReporteRepositorio(db)
    repositorio_registro_retorno = RegistroRetornoRepositorio(db)
    repositorio_registro_retorno_grupo = RegistroRetornoGrupoRepositorio(db)

    return ReportesService(repositorio_colonia =  repositorio_reportes_colonia, 
                           repositorio_usuario = repositorio_reportes_usuario, repositorio_grupo = repositorio_reportes_grupo, 
                           repositorio_persona = repositorio_reportes_persona, repositorio_registro_retorno=repositorio_registro_retorno,
                           repositorio_registro_retorno_grupo = repositorio_registro_retorno_grupo)


router = APIRouter()


@router.get("/reporte-asistencia-colonia/{retorno_id}/{colonia_id}",
            status_code = status.HTTP_200_OK,
            summary = "Generar el informe de asistencia de una colonia a un retorno",
            )
async def generar_reporte_asistencia_colonia(
    request: Request,
    retorno_id: int,
    colonia_id: int,
    servicio: Annotated[ReportesService, Depends(get_reportes_servicio)],
    _: Usuario = Depends(require_roles(2, 3)),
):
    reporte_pdf = await servicio.generar_reporte_asistencia_retorno_colonia(request, colonia_id, retorno_id)
    return reporte_pdf


@router.get("/reporte-general-asistencia/{retorno_id}",
            status_code = status.HTTP_200_OK,
            summary = "Generar el informe de asistencia general de un retorno",
            )
async def generar_reporte_asistencia_general(
    request: Request,
    retorno_id: int,
    servicio: Annotated[ReportesService, Depends(get_reportes_servicio)],
    _: Usuario = Depends(require_roles(2, 3)),
):
    reporte_pdf = await servicio.generar_reporte_general_retorno(request, retorno_id)
    return reporte_pdf
