


from datetime import date

from sqlalchemy import case, func, select, String, extract, Integer, Date

from app.retornos.modelos.persona_grupo_retorno_modelo import persona_grupo_retorno
from app.retornos.modelos.persona_modelo import Persona
from app.retornos.modelos.registro_retorno_grupo_modelo import RegistroRetornoGrupo
from app.retornos.modelos.grupo_retorno_modelo import GrupoRetorno
from app.retornos.modelos.registro_retorno_modelo import RegistroRetorno
from app.retornos.modelos.retorno_grupo_usuario_modelo import Edades
from app.usuarios.models.usuario import Usuario


class PersonaReporteRepositorio:
    def __init__(self, db):
        self.db = db
    
    # La tabla persona no tiene el campo genero
    async def obtener_cantidad_generos_personas_asistentes_por_retorno(self, re_codigo: int):
        stmt = (
            select(Persona.pe_genero, func.count(Persona.pe_codigo).label("cantidad"))
            .join(persona_grupo_retorno, persona_grupo_retorno.pe_codigo == Persona.pe_codigo)
            .join(RegistroRetornoGrupo, RegistroRetornoGrupo.cod_grupo == persona_grupo_retorno.gr_codigo)
            .where(RegistroRetornoGrupo.retorno == re_codigo)
            .group_by(Persona.pe_genero)
        )
        result = await self.db.execute(stmt)
        return {row[0].value: row[1] for row in result.all()}

    
    async def obtener_cantidad_asistentes_por_grupos_edad_retorno(self, re_codigo: int):
        fecha_nac = func.cast(Persona.pe_fecha_nacimiento, Date)
        edad = func.cast(extract('year', func.age(fecha_nac)), Integer)
        edad_grupo = func.cast(case(
            (edad < 18, Edades.menores.value),
            (edad < 60, Edades.adultos.value),
            else_=Edades.adultos_mayores.value
        ), String)
        
        stmt = (
            select(edad_grupo.label("grupo_edad"), func.count(Persona.pe_codigo).label("cantidad"))
            .join(persona_grupo_retorno, persona_grupo_retorno.pe_codigo == Persona.pe_codigo)
            .join(RegistroRetornoGrupo, RegistroRetornoGrupo.cod_grupo == persona_grupo_retorno.gr_codigo)
            .where(RegistroRetornoGrupo.retorno == re_codigo)
            .group_by(edad_grupo)
        )
        result = await self.db.execute(stmt)
        return {row[0]: row[1] for row in result.all()}
    
    async def obtener_cantidad_personas_en_retorno(self, re_codigo: int, co_codigo:int) -> int:
        stmt = (
            select(func.count(Persona.pe_codigo).label("cantidad"))
            .select_from(Persona)
            .join(persona_grupo_retorno, persona_grupo_retorno.pe_codigo == Persona.pe_codigo)
            .join(RegistroRetornoGrupo, RegistroRetornoGrupo.cod_grupo == persona_grupo_retorno.gr_codigo)
            .join(GrupoRetorno, GrupoRetorno.gr_codigo == persona_grupo_retorno.gr_codigo)
            .join(Usuario, Usuario.us_codigo == GrupoRetorno.us_codigo_lider)
            .where(RegistroRetornoGrupo.retorno == re_codigo, Usuario.co_codigo == co_codigo)
        )
        result = await self.db.execute(stmt)
        return result.scalar() or 0
    
    async def obtener_asistentes_colonia_retorno(self, re_codigo: int, co_codigo: int):
        """
        Obtiene personas que asisten a través de grupos a un retorno en una colonia.
        Retorna tuplas (gr_codigo, Persona) para facilitar el agrupamiento.
        """
        stmt = (
            select(persona_grupo_retorno.gr_codigo, Persona)
            .join(persona_grupo_retorno, persona_grupo_retorno.pe_codigo == Persona.pe_codigo)
            .join(RegistroRetornoGrupo, RegistroRetornoGrupo.cod_grupo == persona_grupo_retorno.gr_codigo)
            .join(GrupoRetorno, GrupoRetorno.gr_codigo == RegistroRetornoGrupo.cod_grupo)
            .join(Usuario, Usuario.us_codigo == GrupoRetorno.us_codigo_lider)
            .where(RegistroRetornoGrupo.retorno == re_codigo, Usuario.co_codigo == co_codigo)
        )
        result = await self.db.execute(stmt)
        return [(row[0], row[1]) for row in result.all()]