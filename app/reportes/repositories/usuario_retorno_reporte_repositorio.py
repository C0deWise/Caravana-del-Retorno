



from sqlalchemy import select, func, case
from datetime import date

from app.retornos.modelos.registro_retorno_modelo import RegistroRetorno
from app.usuarios.models.usuario import Usuario




class UsuarioRetornoReporteRepositorio:
    def __init__(self, db):
        self.db = db

    async def obtener_asistentes_detallado_retorno(self, re_codigo: int, co_codigo: int):
        stmt = (
            select(Usuario)
            .join(RegistroRetorno, RegistroRetorno.us_codigo == Usuario.us_codigo)
            .where(RegistroRetorno.retorno == re_codigo and Usuario.colonia == co_codigo)
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()
    
    async def obtener_cantidad_asistentes_detallado_retorno(self, re_codigo: int, co_codigo: int):
        stmt = (
            select(Usuario.us_codigo, func.count(Usuario.us_codigo).label("cantidad"))
            .join(RegistroRetorno, RegistroRetorno.us_codigo == Usuario.us_codigo)
            .where(RegistroRetorno.retorno == re_codigo and Usuario.colonia == co_codigo)
        )
        result = await self.db.execute(stmt)
        return {row[0].value: row[1] for row in result.all()}

    async def obtener_cantidad_generos_usuarios_asistentes_por_retorno(self, re_codigo: int):
        stmt = (
            select(Usuario.us_genero, func.count(Usuario.us_codigo).label("cantidad"))
            .join(RegistroRetorno, RegistroRetorno.usuario == Usuario.us_codigo)
            .where(RegistroRetorno.retorno == re_codigo)
            .group_by(Usuario.us_genero)
        )
        result = await self.db.execute(stmt)
        return {row[0].value: row[1] for row in result.all()}

    async def obtener_cantidad_asistentes_por_grupos_edad_retorno(self, re_codigo: int):
        # Calcular edad y categorizar en grupos
        edad_grupo = case(
            (func.cast((func.julianday(date.today()) - func.julianday(Usuario.us_fecha_nacimiento)) / 365.25, int) < 18, "menores"),
            (func.cast((func.julianday(date.today()) - func.julianday(Usuario.us_fecha_nacimiento)) / 365.25, int) < 60, "adultos"),
            else_="adultos_mayores"
        )
        
        stmt = (
            select(edad_grupo.label("grupo_edad"), func.count(Usuario.us_codigo).label("cantidad"))
            .join(RegistroRetorno, RegistroRetorno.usuario == Usuario.us_codigo)
            .where(RegistroRetorno.retorno == re_codigo)
            .group_by(edad_grupo)
        )
        result = await self.db.execute(stmt)
        return {row[0]: row[1] for row in result.all()}