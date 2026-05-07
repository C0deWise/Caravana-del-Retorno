


import logging

from app.reportes.mapper.mapper import RegistroRetornoGrupoDetalladoMapper, RegistroRetornoIndividualDetalladoMapper
from app.reportes.repositories.colonia_reporte_repositorio import ColoniaReporteRepositorio
from app.reportes.repositories.grupo_retorno_reporte_repositorio import GrupoReportoReporteRepositorio
from app.reportes.repositories.persona_reporte_repositorio import PersonaReporteRepositorio
from app.reportes.repositories.usuario_retorno_reporte_repositorio import UsuarioRetornoReporteRepositorio
from app.retornos.modelos.retorno_grupo_usuario_modelo import Edades
from app.usuarios.models.usuario import Genero

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s — %(name)s — %(levelname)s — %(message)s",
)
logger = logging.getLogger(__name__)

class ReportesService:
    def __init__(self, repositorio_colonia: ColoniaReporteRepositorio, repositorio_usuario: UsuarioRetornoReporteRepositorio, repositorio_grupo: GrupoReportoReporteRepositorio, repositorio_persona: PersonaReporteRepositorio):
        self.repositorio_colonia = repositorio_colonia
        self.repositorio_usuario = repositorio_usuario
        self.repositorio_grupo = repositorio_grupo
        self.repositorio_persona = repositorio_persona

    async def generar_reporte_asistencia_retorno_colonia(self, cod_colonia:int, cod_retorno:int):
        lider_colonia = await self.repositorio_colonia.obtener_lider_colonia(cod_colonia)
        
        # Obtener datos de asistentes
        asistentes_usuario_grupo = await self.repositorio_grupo.obtener_registro_asistentes_detallado_retorno(cod_colonia, cod_retorno)
        asistentes_persona_grupo = await self.repositorio_persona.obtener_asistentes_colonia_retorno(cod_retorno, cod_colonia)
        asistentes_usuario = await self.repositorio_usuario.obtener_asistentes_detallado_retorno(cod_colonia, cod_retorno)
        
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
        return {
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

    async def generar_reporte_general_retorno(self, cod_retorno:int):
        colonias = list(await self.repositorio_colonia.obtener_colonias())
        asistencia_colonia = []
        for colonia in colonias:
            logger.info(f"Colonia:{colonia.co_ciudad}")
            cantidad_asistentes_individuales = await self.repositorio_usuario.obtener_cantidad_asistentes_individuales_retorno(cod_retorno, colonia.co_codigo)
            logger.info(f"cantidad asistentes individuales: {cantidad_asistentes_individuales}" )
            cantidad_asistentes_usuario_grupo = await self.repositorio_grupo.obtener_cantidad_asistentes_retorno(colonia.co_codigo, cod_retorno)
            logger.info(f"cantidad asistente usuario grupo: {cantidad_asistentes_individuales}")
            cantidad_asistentes_persona_grupo = await self.repositorio_persona.obtener_cantidad_personas_en_retorno(cod_retorno, colonia.co_codigo)
            logger.info(f"cantidad asistentes persona grupo: {cantidad_asistentes_individuales}")
            cantidad_asistentes = cantidad_asistentes_individuales + cantidad_asistentes_usuario_grupo + cantidad_asistentes_persona_grupo
            asistencia_colonia.append({
                "colonia": colonia.co_ciudad,
                "cantidad_asistentes": cantidad_asistentes})
            cantidad_asistentes = 0

        asistencia_genero_usuario = await self.repositorio_usuario.obtener_cantidad_generos_usuarios_asistentes_por_retorno(cod_retorno)
        asistencia_genero_usuario_grupo = await self.repositorio_grupo.obtener_cantidad_generos_usuarios_asistentes_por_retorno(cod_retorno)
        #asistencia_genero_persona = await self.repositorio_persona.obtener_cantidad_generos_usuarios_asistentes_por_retorno(cod_retorno)
        generos = list(Genero)
        asistencia_genero = {}
        for genero in generos:
            asistencia_genero[genero] = asistencia_genero_usuario.get(genero, 0) + asistencia_genero_usuario_grupo.get(genero, 0) #+ asistencia_genero_persona.get(genero, 0)

        asistencia_edad_usuario = await self.repositorio_usuario.obtener_cantidad_asistentes_por_grupos_edad_retorno(cod_retorno)
        asistencia_edad_usuario_grupo = await self.repositorio_grupo.obtener_cantidad_asistentes_por_grupos_edad_retorno(cod_retorno)
        asistencia_edad_persona = await self.repositorio_persona.obtener_cantidad_asistentes_por_grupos_edad_retorno(cod_retorno)
        grupos_edad = list(Edades)
        asistencia_edad = {}
        for grupo in grupos_edad:
            asistencia_edad[grupo] = asistencia_edad_usuario.get(grupo, 0) + asistencia_edad_usuario_grupo.get(grupo, 0) + asistencia_edad_persona.get(grupo, 0)
        
        return {
            "asistencia_colonia": asistencia_colonia,
            "asistencia_genero": asistencia_genero,
            "asistencia_edad": asistencia_edad
        }
