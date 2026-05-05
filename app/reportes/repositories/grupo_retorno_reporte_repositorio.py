



from datetime import date

from sqlalchemy import case, func, select

from app.retornos.modelos.registro_retorno_grupo_modelo import RegistroRetornoGrupo
from app.retornos.modelos.retorno_grupo_usuario_modelo import RetornoGrupoUsuario
from app.usuarios.models.usuario import Usuario


class GrupoReportoReporteRepositorio:
    def __init__(self, db):
        self.db = db

    async def obtener_registro_asistentes_detallado_retorno(self, co_codigo:int, re_codigo: int):
        stmt = (
            select(Usuario)
            .join(RetornoGrupoUsuario, RetornoGrupoUsuario.usuario == Usuario.us_codigo)
            .join(RegistroRetornoGrupo, RegistroRetornoGrupo.cod_grupo == RetornoGrupoUsuario.gr_codigo)
            .where(RegistroRetornoGrupo.retorno == re_codigo and Usuario.colonia == co_codigo)
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()
    
    async def obtener_cantidad_grupos_retorno(self, re_codigo: int):
        stmt = (
            select(func.count(RegistroRetornoGrupo.cod_grupo).label("cantidad"))
            .where(RegistroRetornoGrupo.retorno == re_codigo)
        )
        result = await self.db.execute(stmt)
        return result.scalar()

    async def obtener_cantidad_asistentes_retorno(self, co_codigo:int, re_codigo: int):
        stmt = (
            select(Usuario.us_codigo,func.count(Usuario.us_codigo).label("cantidad"))
            .join(RetornoGrupoUsuario, RetornoGrupoUsuario.usuario == Usuario.us_codigo)
            .join(RegistroRetornoGrupo, RegistroRetornoGrupo.cod_grupo == RetornoGrupoUsuario.gr_codigo)
            .where(RegistroRetornoGrupo.retorno == re_codigo and Usuario.colonia == co_codigo)
        )
        result = await self.db.execute(stmt)
        return {row[0].value: row[1] for row in result.all()}
    
    async def obtener_cantidad_generos_usuarios_asistentes_por_retorno(self, re_codigo: int):
        stmt = (
            select(Usuario.us_genero, func.count(Usuario.us_codigo).label("cantidad"))
            .join(RetornoGrupoUsuario, RetornoGrupoUsuario.usuario == Usuario.us_codigo)
            .join(RegistroRetornoGrupo, RegistroRetornoGrupo.cod_grupo == RetornoGrupoUsuario.gr_codigo)
            .where(RegistroRetornoGrupo.retorno == re_codigo)
            .group_by(Usuario.us_genero)
        )
        result = await self.db.execute(stmt)
        return {row[0].value: row[1] for row in result.all()}

    async def obtener_cantidad_asistentes_por_grupos_edad_retorno(self, re_codigo: int):
        edad_grupo = case(
            (func.cast((func.julianday(date.today()) - func.julianday(Usuario.us_fecha_nacimiento)) / 365.25, int) < 18, "menores"),
            (func.cast((func.julianday(date.today()) - func.julianday(Usuario.us_fecha_nacimiento)) / 365.25, int) < 60, "adultos"),
            else_="adultos_mayores"
        )
        
        stmt = (
            select(edad_grupo.label("grupo_edad"), func.count(Usuario.us_codigo).label("cantidad"))
            .join(RetornoGrupoUsuario, RetornoGrupoUsuario.usuario == Usuario.us_codigo)
            .join(RegistroRetornoGrupo, RegistroRetornoGrupo.cod_grupo == RetornoGrupoUsuario.gr_codigo)
            .where(RegistroRetornoGrupo.retorno == re_codigo)
            .group_by(edad_grupo)
        )
        result = await self.db.execute(stmt)
        return {row[0]: row[1] for row in result.all()}