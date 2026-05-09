
"""
gupo_retorno_reporte_repositorio.py
===================================
Propósito: Repositorio de datos para obtener información de grupos de retorno.
          Consulta información sobre grupos de retorno, sus líderes y asistentes,
          incluyendo necesidades de transporte y hospedaje a nivel de grupo.
"""

from datetime import date

from sqlalchemy import case, func, select, String, extract, Integer, Date
from sqlalchemy.orm import selectinload

from app.retornos.modelos.registro_retorno_grupo_modelo import RegistroRetornoGrupo
from app.retornos.modelos.retorno_grupo_usuario_modelo import Edades, RetornoGrupoUsuario
from app.retornos.modelos.grupo_retorno_modelo import GrupoRetorno
from app.usuarios.models.usuario import Usuario


class GrupoReportoReporteRepositorio:
    def __init__(self, db):
        self.db = db

    async def obtener_registros_retorno_grupo(self, re_codigo: int, co_codigo: int):
        """
        Obtiene todos los registros de grupos para un retorno,
        cargando las relaciones necesarias para el mapper.
        
        Args:
            re_codigo: Código del retorno
            co_codigo: Código de la colonia
            
        Returns:
            Lista de RegistroRetornoGrupo con grupo_retorno_rel cargado
        """
        stmt = (
            select(RegistroRetornoGrupo)
            .join(GrupoRetorno, GrupoRetorno.gr_codigo == RegistroRetornoGrupo.cod_grupo)
            .join(Usuario, Usuario.us_codigo == GrupoRetorno.us_codigo_lider)
            .where(RegistroRetornoGrupo.retorno == re_codigo, Usuario.co_codigo == co_codigo)
            .options(
                selectinload(RegistroRetornoGrupo.grupo_retorno_rel).selectinload(GrupoRetorno.lider)
            )
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def obtener_registro_asistentes_detallado_retorno(self, co_codigo:int, re_codigo: int):
        """
        Obtiene usuarios que asisten a través de grupos a un retorno en una colonia.
        Retorna tuplas (gr_codigo, Usuario) para facilitar el agrupamiento.
        """
        stmt = (
            select(RegistroRetornoGrupo.cod_grupo, Usuario)
            .select_from(RetornoGrupoUsuario)
            .join(Usuario, Usuario.us_codigo == RetornoGrupoUsuario.us_codigo)
            .join(RegistroRetornoGrupo, RegistroRetornoGrupo.cod_grupo == RetornoGrupoUsuario.gr_codigo)
            .where(RegistroRetornoGrupo.retorno == re_codigo, Usuario.co_codigo == co_codigo)
        )
        result = await self.db.execute(stmt)
        return [(row[0], row[1]) for row in result.all()]
    
    async def obtener_total_necesidades_retorno(self, co_codigo:int, re_codigo: int):
        stmt = (
            select(
                func.sum(RegistroRetornoGrupo.num_hospedaje).label("total_hospedaje"),
                func.sum(RegistroRetornoGrupo.num_transporte).label("total_transporte"),
                func.sum(RegistroRetornoGrupo.num_parqueadero_carro).label("total_parqueadero_carros"),
                func.sum(RegistroRetornoGrupo.num_parqueadero_moto).label("total_parqueadero_motos")
            )
            .join(GrupoRetorno, GrupoRetorno.gr_codigo == RegistroRetornoGrupo.cod_grupo)
            .join(Usuario, Usuario.us_codigo == GrupoRetorno.us_codigo_lider)
            .where(RegistroRetornoGrupo.retorno == re_codigo, Usuario.co_codigo == co_codigo)
        )
        result = await self.db.execute(stmt)
        return result.fetchone() or (0, 0, 0, 0)

    async def obtener_cantidad_grupos_retorno(self, re_codigo: int, co_codigo: int):
        stmt = (
            select(func.count(RegistroRetornoGrupo.cod_grupo).label("cantidad"))
            .join(GrupoRetorno, GrupoRetorno.gr_codigo == RegistroRetornoGrupo.cod_grupo)
            .join(Usuario, Usuario.us_codigo == GrupoRetorno.us_codigo_lider)
            .where(RegistroRetornoGrupo.retorno == re_codigo, Usuario.co_codigo == co_codigo)
        )
        result = await self.db.execute(stmt)
        return result.scalar()

    async def obtener_cantidad_asistentes_retorno(self, co_codigo:int, re_codigo: int):
        stmt = (
            select(func.count(Usuario.us_codigo).label("cantidad"))
            .join(RetornoGrupoUsuario, RetornoGrupoUsuario.us_codigo == Usuario.us_codigo)
            .join(RegistroRetornoGrupo, RegistroRetornoGrupo.cod_grupo == RetornoGrupoUsuario.gr_codigo)
            .where(RegistroRetornoGrupo.retorno == re_codigo, Usuario.co_codigo == co_codigo)
        )
        result = await self.db.execute(stmt)
        return result.scalar() or 0
    
    async def obtener_cantidad_generos_usuarios_asistentes_por_retorno(self, re_codigo: int):
        stmt = (
            select(Usuario.us_genero, func.count(Usuario.us_codigo).label("cantidad"))
            .join(RetornoGrupoUsuario, RetornoGrupoUsuario.us_codigo == Usuario.us_codigo)
            .join(RegistroRetornoGrupo, RegistroRetornoGrupo.cod_grupo == RetornoGrupoUsuario.gr_codigo)
            .where(RegistroRetornoGrupo.retorno == re_codigo)
            .group_by(Usuario.us_genero)
        )
        result = await self.db.execute(stmt)
        return {row[0].value: row[1] for row in result.all()}

    async def obtener_cantidad_asistentes_por_grupos_edad_retorno(self, re_codigo: int):
        fecha_nac = func.cast(Usuario.us_fecha_nacimiento, Date)
        edad = func.cast(extract('year', func.age(fecha_nac)), Integer)
        edad_grupo = func.cast(case(
            (edad < 18, Edades.menores.value),
            (edad < 60, Edades.adultos.value),
            else_=Edades.adultos_mayores.value
        ), String)
        
        stmt = (
            select(edad_grupo.label("grupo_edad"), func.count(Usuario.us_codigo).label("cantidad"))
            .join(RetornoGrupoUsuario, RetornoGrupoUsuario.us_codigo == Usuario.us_codigo)
            .join(RegistroRetornoGrupo, RegistroRetornoGrupo.cod_grupo == RetornoGrupoUsuario.gr_codigo)
            .where(RegistroRetornoGrupo.retorno == re_codigo)
            .group_by(edad_grupo)
        )
        result = await self.db.execute(stmt)
        return {row[0]: row[1] for row in result.all()}