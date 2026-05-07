



from sqlalchemy import select, func, case, String, extract, Integer, Date
from datetime import date

from app.retornos.modelos.registro_retorno_modelo import RegistroRetorno
from app.retornos.modelos.retorno_grupo_usuario_modelo import Edades
from app.usuarios.models.usuario import Usuario




class UsuarioRetornoReporteRepositorio:
    def __init__(self, db):
        self.db = db

    async def obtener_asistentes_detallado_retorno(self, re_codigo: int, co_codigo: int):
        stmt = (
            select(Usuario, RegistroRetorno)
            .join(RegistroRetorno, RegistroRetorno.usuario == Usuario.us_codigo)
            .where(RegistroRetorno.retorno == re_codigo, Usuario.co_codigo == co_codigo)
        )
        result = await self.db.execute(stmt)
        return result.all()
    
    async def obtener_cantidad_asistentes_individuales_retorno(self, re_codigo: int, co_codigo: int):
        stmt = (
            select(func.count(Usuario.us_codigo).label("cantidad"))
            .join(RegistroRetorno, RegistroRetorno.usuario == Usuario.us_codigo)
            .where(RegistroRetorno.retorno == re_codigo, Usuario.co_codigo == co_codigo)
        )
        result = await self.db.execute(stmt)
        return result.scalar() or 0

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
        fecha_nac = func.cast(Usuario.us_fecha_nacimiento, Date)
        edad = func.cast(extract('year', func.age(fecha_nac)), Integer)
        edad_grupo = func.cast(case(
            (edad < 18, Edades.menores.value),
            (edad < 60, Edades.adultos.value),
            else_=Edades.adultos_mayores.value
        ), String)
        
        stmt = (
            select(edad_grupo.label("grupo_edad"), func.count(Usuario.us_codigo).label("cantidad"))
            .join(RegistroRetorno, RegistroRetorno.usuario == Usuario.us_codigo)
            .where(RegistroRetorno.retorno == re_codigo)
            .group_by(edad_grupo)
        )
        result = await self.db.execute(stmt)
        return {row[0]: row[1] for row in result.all()}