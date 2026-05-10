
"""
usuario_retorno_reporte_repositorio.py
======================================
Propósito: Repositorio de datos para obtener información de asistentes individuales a retornos.
          Consulta la base de datos para obtener detalles de usuarios que asisten de forma
          individual y sus necesidades de hospedaje, transporte y parqueadero.
"""

from sqlalchemy import select, func, case, String, extract, Integer, Date
from datetime import date

import logging

from app.retornos.modelos.registro_retorno_modelo import RegistroRetorno
from app.retornos.modelos.retorno_grupo_usuario_modelo import Edades
from app.usuarios.models.usuario import Usuario


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s — %(name)s — %(levelname)s — %(message)s",
)
logger = logging.getLogger(__name__)

class UsuarioRetornoReporteRepositorio:
    def __init__(self, db):
        self.db = db

    async def obtener_asistentes_detallado_retorno(self, re_codigo: int, co_codigo: int):
        stmt = (
            select(Usuario, RegistroRetorno)
            .join(RegistroRetorno, RegistroRetorno.usuario == Usuario.us_codigo)
            .where(RegistroRetorno.retorno == re_codigo, Usuario.co_codigo == co_codigo)
        )
        logger.info(stmt.compile(compile_kwargs={"literal_binds": True}))
        result = await self.db.execute(stmt)
        return result.all()
    
    async def obtener_necesidades_totales_retorno(self, re_codigo: int, co_codigo: int):
        stmt = (
            select(
                func.sum(RegistroRetorno.num_hospedaje).label("total_hospedaje"),
                func.sum(RegistroRetorno.num_transporte).label("total_transporte"),
                func.sum(RegistroRetorno.num_parqueadero_carro).label("total_parqueadero_carros"),
                func.sum(RegistroRetorno.num_parqueadero_moto).label("total_parqueadero_motos")
            )
            .join(Usuario, Usuario.us_codigo == RegistroRetorno.usuario)
            .where(RegistroRetorno.retorno == re_codigo, Usuario.co_codigo == co_codigo)
        )
        logger.info(stmt.compile(compile_kwargs={"literal_binds": True}))
        result = await self.db.execute(stmt)
        return result.first()
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