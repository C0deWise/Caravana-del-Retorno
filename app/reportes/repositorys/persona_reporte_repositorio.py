


from sqlalchemy import select

from app.retornos.modelos.persona_grupo_retorno_modelo import persona_grupo_retorno
from app.retornos.modelos.registro_retorno_grupo_modelo import RegistroRetornoGrupo


class PersonaReporteRepositorio:
    def __init__(self, db):
        self.db = db
    

    def obtener_cantidad_generos_usuarios_asistentes_por_retorno(self, re_codigo: int):
        pass

    def obtener_cantidad_asistentes_por_grupos_edad_retorno(self, re_codigo: int):
        pass
    async def obtener_cantidad_personas_en_retorno(self, re_codigo: int) -> int:
        stmt = (
            select(persona_grupo_retorno)
            .join(RegistroRetornoGrupo, persona_grupo_retorno.gr_codigo == RegistroRetornoGrupo.cod_grupo)
            .where(RegistroRetornoGrupo.retorno == re_codigo)
        )
        result = await self.db.execute(stmt)
        return len(result.scalars().all())