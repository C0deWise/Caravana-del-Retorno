

from app.reportes.repositories.colonia_reporte_repositorio import ColoniaReporteRepositorio
from app.reportes.repositories.grupo_retorno_reporte_repositorio import GrupoReportoReporteRepositorio
from app.reportes.repositories.persona_reporte_repositorio import PersonaReporteRepositorio
from app.reportes.repositories.usuario_retorno_reporte_repositorio import UsuarioRetornoReporteRepositorio


class ReportesService:
    def __init__(self, repositorio_colonia: ColoniaReporteRepositorio, repositorio_usuario: UsuarioRetornoReporteRepositorio, repositorio_grupo: GrupoReportoReporteRepositorio, repositorio_persona: PersonaReporteRepositorio):
        self.repositorio_colonia = repositorio_colonia
        self.repositorio_usuario = repositorio_usuario
        self.repositorio_grupo = repositorio_grupo
        self.repositorio_persona = repositorio_persona

    def generar_reporte_asistencia_retorno_colonia(self, cod_colonia:int, cod_retorno:int):
        lider_colonia = self.repositorio_colonia.obtener_lider_colonia(cod_colonia)
        
        asistentes_usuario_grupo = self.repositorio_grupo.obtener_registro_asistentes_detallado_retorno(cod_colonia, cod_retorno)
        asistentes_persona_grupo = self.repositorio_persona.obtener_asistentes_colonia_retorno(cod_retorno, cod_colonia)
        asistentes_grupos = asistentes_usuario_grupo + asistentes_persona_grupo
        asistentes_usuario = self.repositorio_usuario.obtener_registro_asistentes_detallado_retorno(cod_colonia, cod_retorno)
        cantidad_total_asistentes = len(asistentes_usuario) + len(asistentes_usuario_grupo) + len(asistentes_persona_grupo)
        cantidad_total_invitados = len(asistentes_persona_grupo)
        cantidad_asistentes_individuales = len(asistentes_usuario)
        cantidad_grupos = self.repositorio_grupo.obtener_cantidad_grupos_retorno(cod_retorno)

    def generar_reporte_general_retorno(self, cod_retorno:int):
        colonias = self.repositorio_colonia.obtener_colonias()
        asistencia_colonia = []
        for colonia in colonias:
            cantidad_asistentes_usuario = self.repositorio_usuario.obtener_cantidad_asistentes_detallado_retorno(cod_retorno, colonia.co_codigo)
            cantidad_asistentes_usuario_grupo = self.repositorio_grupo.obtener_cantidad_asistentes_retorno(colonia.co_codigo, cod_retorno)
            cantidad_asistentes_persona_grupo = self.repositorio_persona.obtener_cantidad_personas_en_retorno(cod_retorno)
            cantidad_asistentes = cantidad_asistentes_usuario + cantidad_asistentes_usuario_grupo + cantidad_asistentes_persona_grupo
            asistencia_colonia.append({
                "colonia": colonia.co_nombre,
                "cantidad_asistentes": cantidad_asistentes})

        asistencia_genero_usuario = self.repositorio_usuario.obtener_cantidad_generos_usuarios_asistentes_por_retorno(cod_retorno)
        asistencia_genero_usuario_grupo = self.repositorio_grupo.obtener_cantidad_generos_usuarios_asistentes_por_retorno(cod_retorno)
        asistencia_genero_persona = self.repositorio_persona.obtener_cantidad_generos_usuarios_asistentes_por_retorno(cod_retorno)
        generos = asistencia_genero_usuario.keys()
        asistencia_genero = {}
        for genero in generos:
            asistencia_genero[genero] = asistencia_genero_usuario.get(genero, 0) + asistencia_genero_usuario_grupo.get(genero, 0) + asistencia_genero_persona.get(genero, 0)

        asistencia_edad_usuario = self.repositorio_usuario.obtener_cantidad_asistentes_por_grupos_edad_retorno(cod_retorno)
        asistencia_edad_usuario_grupo = self.repositorio_grupo.obtener_cantidad_asistentes_por_grupos_edad_retorno(cod_retorno)
        asistencia_edad_persona = self.repositorio_persona.obtener_cantidad_asistentes_por_grupos_edad_retorno(cod_retorno)
        grupos_edad = asistencia_edad_usuario.keys()
        asistencia_edad = {}
        for grupo in grupos_edad:
            asistencia_edad[grupo] = asistencia_edad_usuario.get(grupo, 0) + asistencia_edad_usuario_grupo.get(grupo, 0) + asistencia_edad_persona.get(grupo, 0)
