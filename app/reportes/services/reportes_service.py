
"""
reportes_service.py
==================
Propósito: Servicio de negocio para la generación de reportes de retornos.
          Coordina la obtención de datos de múltiples repositorios, mapea la información
          y genera reportes PDF con asistencia, necesidades y estadísticas de retornos.
"""

import logging

from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.colonias.excepciones.excepciones import ColoniaNoExistente
from app.reportes.mapper.mapper import RegistroRetornoGrupoDetalladoMapper, RegistroRetornoIndividualDetalladoMapper
from app.reportes.models.necesidades_totales_modelo import NecesidadesTotales
from app.reportes.repositories.colonia_reporte_repositorio import ColoniaReporteRepositorio
from app.reportes.repositories.grupo_retorno_reporte_repositorio import GrupoReportoReporteRepositorio
from app.reportes.repositories.persona_reporte_repositorio import PersonaReporteRepositorio
from app.reportes.repositories.usuario_retorno_reporte_repositorio import UsuarioRetornoReporteRepositorio
from app.reportes.utils.pdf_utils import render_to_pdf
from app.retornos.excepciones.registro_retorno_excepciones import NoHayColonias, RetornoNoExistente
from app.retornos.modelos.retorno_grupo_usuario_modelo import Edades
from app.usuarios.models.usuario import Genero

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s — %(name)s — %(levelname)s — %(message)s",
)
logger = logging.getLogger(__name__)

templates = Jinja2Templates(directory="app/reportes/templates")

class ReportesService:
    def __init__(self, repositorio_colonia: ColoniaReporteRepositorio, repositorio_usuario: UsuarioRetornoReporteRepositorio, repositorio_grupo: GrupoReportoReporteRepositorio, repositorio_persona: PersonaReporteRepositorio):
        self.repositorio_colonia = repositorio_colonia
        self.repositorio_usuario = repositorio_usuario
        self.repositorio_grupo = repositorio_grupo
        self.repositorio_persona = repositorio_persona

    async def generar_reporte_asistencia_retorno_colonia(self, request: Request, cod_colonia:int, cod_retorno:int):
       
        retorno = await self.repositorio_colonia.obtener_retorno(cod_retorno)
        if retorno is None:
            raise RetornoNoExistente(cod_retorno)
        colonia = await self.repositorio_colonia.obtener_colonia(cod_colonia)
        if colonia is None:
            raise ColoniaNoExistente(cod_colonia)
        lider_colonia = await self.repositorio_colonia.obtener_lider_colonia(cod_colonia)
        colonia = await self.repositorio_colonia.obtener_colonia(cod_colonia)
        retorno = await self.repositorio_colonia.obtener_retorno(cod_retorno)
        
        # Obtener datos de asistentes
        asistentes_usuario_grupo = await self.repositorio_grupo.obtener_registro_asistentes_detallado_retorno(cod_colonia, cod_retorno)
        asistentes_persona_grupo = await self.repositorio_persona.obtener_asistentes_colonia_retorno(cod_retorno, cod_colonia)
        asistentes_usuario = await self.repositorio_usuario.obtener_asistentes_detallado_retorno(cod_retorno, cod_colonia)
        
        logger.info(f"asistentes usuario grupo, colonia {cod_colonia}: usuarios: {asistentes_usuario_grupo}")
        logger.info(f"asistentes persona grupo, colonia {cod_colonia}: usuarios: {asistentes_persona_grupo}")
        logger.info(f"asistentes usuario, colonia {cod_colonia}: usuarios: {asistentes_usuario}")
        # Calcular cantidades
        cantidad_total_asistentes = len(asistentes_usuario) + len(asistentes_usuario_grupo) + len(asistentes_persona_grupo)
        cantidad_total_invitados = len(asistentes_persona_grupo)
        cantidad_usuarios_en_grupo = len(asistentes_usuario_grupo)
        cantidad_asistentes_grupo = len(asistentes_persona_grupo) + len(asistentes_usuario_grupo)
        cantidad_asistentes_individuales = len(asistentes_usuario)
        cantidad_grupos = await self.repositorio_grupo.obtener_cantidad_grupos_retorno(cod_retorno, cod_colonia)

        # Obtener registros de grupos para mapeo
        registros_grupos = await self.repositorio_grupo.obtener_registros_retorno_grupo(cod_retorno,cod_colonia)

        # Mapear con asistentes
        reportes_grupos = RegistroRetornoGrupoDetalladoMapper.mapear_grupos_con_asistentes(
            registros_grupos,
            asistentes_usuario_grupo,
            asistentes_persona_grupo
        )
        reportes_individuales = RegistroRetornoIndividualDetalladoMapper.mapear_usuarios_asistentes(asistentes_usuario)
        print (reportes_grupos)
        respuesta = {
            "lider": lider_colonia,
            "cantidad_usuarios_en_grupo": cantidad_usuarios_en_grupo,
            "cantidad_total_asistentes": cantidad_total_asistentes,
            "cantidad_total_asistentes_grupo": cantidad_asistentes_grupo,
            "cantidad_total_invitados": cantidad_total_invitados,
            "cantidad_asistentes_individuales": cantidad_asistentes_individuales,
            "cantidad_grupos": cantidad_grupos,
            "reportes_grupos": reportes_grupos,
            "reportes_individuales": reportes_individuales
            }
        
        necesidades_totales_individuales = await self.repositorio_usuario.obtener_necesidades_totales_retorno(cod_retorno, cod_colonia)
        logger.info(f"Necesidades totales individuales: {necesidades_totales_individuales._mapping}")
        logger.info(f"necesidades_totales_individuales._mapping.keys(): {list(necesidades_totales_individuales._mapping.keys())}")
        necesidades_totales_grupo = await self.repositorio_grupo.obtener_total_necesidades_retorno(cod_colonia, cod_retorno)
        total_hospedaje = (necesidades_totales_individuales.total_hospedaje or 0) + (necesidades_totales_grupo.total_hospedaje or 0)
        total_transporte = (necesidades_totales_individuales.total_transporte or 0) + (necesidades_totales_grupo.total_transporte or 0)
        total_pc = (necesidades_totales_individuales.total_parqueadero_carros or 0) + (necesidades_totales_grupo.total_parqueadero_carros or 0)
        total_pm = (necesidades_totales_individuales.total_parqueadero_motos or 0) + (necesidades_totales_grupo.total_parqueadero_motos or 0)
        logger.info(f"total necesidades - hospedaje: {total_hospedaje}, transporte: {total_transporte}, parqueadero carros: {total_pc}, parqueadero motos: {total_pm}")
        necesidades_totales = NecesidadesTotales(num_parqueadero_motos=total_pm, num_parqueadero_carros=total_pc, num_hospedaje=total_hospedaje, num_transporte=total_transporte)
        logger.info(f"Reporte colonia {cod_colonia} — retorno {cod_retorno} generado.")
 
        context = {
            "request":                        request,
            "colonia":                        colonia,
            "necesidades_totales":            necesidades_totales,
            "retorno":                         retorno,
            "lider":                          lider_colonia,
            "cantidad_usuarios_en_grupo":     cantidad_usuarios_en_grupo,
            "cantidad_total_asistentes":      cantidad_total_asistentes,
            "cantidad_total_asistentes_grupo": cantidad_asistentes_grupo,
            "cantidad_total_invitados":       cantidad_total_invitados,
            "cantidad_asistentes_individuales": cantidad_asistentes_individuales,
            "cantidad_grupos":                cantidad_grupos,
            "reportes_grupos":                reportes_grupos,
            "reportes_individuales":          reportes_individuales,
        }
 
        #return templates.TemplateResponse("reporte_colonia.html", context)
        return render_to_pdf(
            templates=templates,
            template_name="reporte_colonia.html",
            context=context,
            filename=f"reporte_colonia_{cod_colonia}_retorno_{cod_retorno}.pdf",
        )

    async def generar_reporte_general_retorno(self, request: Request,cod_retorno:int):
        retorno = await self.repositorio_colonia.obtener_retorno(cod_retorno)
        if retorno is None:
            raise RetornoNoExistente(cod_retorno)
        
        colonias = list(await self.repositorio_colonia.obtener_colonias())
        if colonias is None or len(colonias) == 0:
            raise NoHayColonias()
        
        asistencia_colonia = []
        for colonia in colonias:
            logger.info(f"Colonia:{colonia.ciudad}")
            cantidad_asistentes_individuales = await self.repositorio_usuario.obtener_cantidad_asistentes_individuales_retorno(cod_retorno, colonia.codigo)
            logger.info(f"cantidad asistentes individuales: {cantidad_asistentes_individuales}" )
            cantidad_asistentes_usuario_grupo = await self.repositorio_grupo.obtener_cantidad_asistentes_retorno(colonia.codigo, cod_retorno)
            logger.info(f"cantidad asistente usuario grupo: {cantidad_asistentes_individuales}")
            cantidad_asistentes_persona_grupo = await self.repositorio_persona.obtener_cantidad_personas_en_retorno(cod_retorno, colonia.codigo)
            logger.info(f"cantidad asistentes persona grupo: {cantidad_asistentes_individuales}")
            cantidad_asistentes = cantidad_asistentes_individuales + cantidad_asistentes_usuario_grupo + cantidad_asistentes_persona_grupo
            asistencia_colonia.append({
                "colonia": colonia.ciudad,
                "cantidad_asistentes": cantidad_asistentes})
            cantidad_asistentes = 0

        asistencia_genero_usuario = await self.repositorio_usuario.obtener_cantidad_generos_usuarios_asistentes_por_retorno(cod_retorno)
        asistencia_genero_usuario_grupo = await self.repositorio_grupo.obtener_cantidad_generos_usuarios_asistentes_por_retorno(cod_retorno)
        asistencia_genero_persona = await self.repositorio_persona.obtener_cantidad_generos_personas_asistentes_por_retorno(cod_retorno)
        generos = list(Genero)
        asistencia_genero = {}
        for genero in generos:
            asistencia_genero[genero] = asistencia_genero_usuario.get(genero, 0) + asistencia_genero_usuario_grupo.get(genero, 0) + asistencia_genero_persona.get(genero, 0)

        asistencia_edad_usuario = await self.repositorio_usuario.obtener_cantidad_asistentes_por_grupos_edad_retorno(cod_retorno)
        asistencia_edad_usuario_grupo = await self.repositorio_grupo.obtener_cantidad_asistentes_por_grupos_edad_retorno(cod_retorno)
        asistencia_edad_persona = await self.repositorio_persona.obtener_cantidad_asistentes_por_grupos_edad_retorno(cod_retorno)
        grupos_edad = list(Edades)
        asistencia_edad = {}
        for grupo in grupos_edad:
            asistencia_edad[grupo] = asistencia_edad_usuario.get(grupo, 0) + asistencia_edad_usuario_grupo.get(grupo, 0) + asistencia_edad_persona.get(grupo, 0)
        
        respuesta = {
            "asistencia_colonia": asistencia_colonia,
            "asistencia_genero": asistencia_genero,
            "asistencia_edad": asistencia_edad
            }
        
        logger.info(f"Reporte general — retorno {cod_retorno} generado.")
 
        context = {
            "request":           request,
            "asistencia_colonia": asistencia_colonia,
            "asistencia_genero":  asistencia_genero,
            "asistencia_edad":    asistencia_edad,
        }
 
        #return templates.TemplateResponse("reporte_general.html", context)
        return render_to_pdf(
            templates=templates,
            template_name="reporte_general.html",
            context=context,
            filename=f"reporte_general_retorno_{cod_retorno}.pdf",
        )
