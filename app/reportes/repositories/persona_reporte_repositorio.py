


from datetime import date

from sqlalchemy import case, func, select

from app.retornos.modelos.persona_grupo_retorno_modelo import persona_grupo_retorno
from app.retornos.modelos.persona_modelo import Persona
from app.retornos.modelos.registro_retorno_grupo_modelo import RegistroRetornoGrupo
from app.retornos.modelos.registro_retorno_modelo import RegistroRetorno
from app.usuarios.models.usuario import Usuario


class PersonaReporteRepositorio:
    def __init__(self, db):
        self.db = db
    

    async def obtener_cantidad_generos_usuarios_asistentes_por_retorno(self, re_codigo: int):
        stmt = (
            select(Persona.pe_genero, func.count(Persona.pe_codigo).label("cantidad"))
            .join(RegistroRetorno, RegistroRetorno.usuario == Usuario.us_codigo)
            .where(RegistroRetorno.retorno == re_codigo)
            .group_by(Usuario.us_genero)
        )
        result = await self.db.execute(stmt)
        return {row[0].value: row[1] for row in result.all()}

    async def obtener_cantidad_asistentes_por_grupos_edad_retorno(self, re_codigo: int):
        edad_grupo = case(
            (func.cast((func.julianday(date.today()) - func.julianday(Persona.pe_fecha_nacimiento)) / 365.25, int) < 18, "menores"),
            (func.cast((func.julianday(date.today()) - func.julianday(Persona.pe_fecha_nacimiento)) / 365.25, int) < 60, "adultos"),
            else_="adultos_mayores"
        )
        
        stmt = (
            select(edad_grupo.label("grupo_edad"), func.count(Persona.pe_codigo).label("cantidad"))
            .join(persona_grupo_retorno, persona_grupo_retorno.persona == Persona.pe_codigo)
            .join(RegistroRetornoGrupo, RegistroRetornoGrupo.cod_grupo == persona_grupo_retorno.gr_codigo)
            .where(RegistroRetornoGrupo.retorno == re_codigo)
            .group_by(edad_grupo)
        )
        result = await self.db.execute(stmt)
        return {row[0]: row[1] for row in result.all()}
    
    async def obtener_cantidad_personas_en_retorno(self, re_codigo: int) -> int:
        stmt = (
            select(persona_grupo_retorno)
            .join(RegistroRetornoGrupo, persona_grupo_retorno.gr_codigo == RegistroRetornoGrupo.cod_grupo)
            .where(RegistroRetornoGrupo.retorno == re_codigo)
        )
        result = await self.db.execute(stmt)
        return len(result.scalars().all())
    
    async def obtener_asistentes_colonia_retorno(self, re_codigo: int, co_codigo: int):
        stmt = (
            select(Persona)
            .join(persona_grupo_retorno, persona_grupo_retorno.persona == Persona.pe_codigo)
            .join(RegistroRetornoGrupo, RegistroRetornoGrupo.cod_grupo == persona_grupo_retorno.gr_codigo)
            .where(RegistroRetornoGrupo.retorno == re_codigo and RegistroRetornoGrupo.grupo_retorno_rel.lider.co_codigo == co_codigo)
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()