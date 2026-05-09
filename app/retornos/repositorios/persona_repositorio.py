"""
    persona_repositorio.py se encarga de la gestion de las personas que no son usuarios del sistema, 
    pero asisten a los retornos mediante los grupos de retorno. 
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.retornos.modelos.persona_modelo import Persona
from app.retornos.modelos.persona_grupo_retorno_modelo import persona_grupo_retorno
from app.retornos.modelos.registro_retorno_grupo_modelo import RegistroRetornoGrupo
from app.retornos.esquemas.persona_esquema import PersonaCrear
from typing import List, Optional

class PersonaRepositorio:
    """
    Repositorio para gestionar las operaciones relacionadas con las personas en el sistema de retorno.
    """
    def __init__(self, db: AsyncSession):
        self.db = db

    async def crear_persona(self, datos: PersonaCrear) -> Persona:
        """
        Crea una nueva persona en la base de datos.
        """
        nueva_persona = Persona(
            pe_tipo_doc=datos.pe_tipo_doc,
            pe_documento=datos.pe_documento,
            pe_nombre=datos.pe_nombre,
            pe_apellido=datos.pe_apellido,
            pe_correo=datos.pe_correo,
            pe_fecha_nacimiento=datos.pe_fecha_nacimiento
        )
        self.db.add(nueva_persona)
        await self.db.commit()
        await self.db.refresh(nueva_persona)
        return nueva_persona

    async def obtener_por_documento(self, documento: str) -> Optional[Persona]:
        result = await self.db.execute(select(Persona).where(Persona.pe_documento == documento))
        return result.scalars().first()

    async def obtener_por_correo(self, correo: str) -> Optional[Persona]:
        if not correo: return None
        result = await self.db.execute(select(Persona).where(Persona.pe_correo == correo))
        return result.scalars().first()

    async def obtener_por_id(self, pe_codigo: int) -> Optional[Persona]:
        result = await self.db.execute(select(Persona).where(Persona.pe_codigo == pe_codigo))
        return result.scalars().first()

    async def asociar_a_grupo(self, pe_codigo: int, gr_codigo: int) -> persona_grupo_retorno:
        nueva_asociacion = persona_grupo_retorno(pe_codigo=pe_codigo, gr_codigo=gr_codigo)
        self.db.add(nueva_asociacion)
        await self.db.commit()
        await self.db.refresh(nueva_asociacion)
        return nueva_asociacion

    async def obtener_personas_por_grupo(self, gr_codigo: int) -> List[Persona]:
        stmt = (
            select(Persona)
            .join(persona_grupo_retorno, Persona.pe_codigo == persona_grupo_retorno.pe_codigo)
            .where(persona_grupo_retorno.gr_codigo == gr_codigo)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def persona_ya_en_retorno(self, pe_codigo: int, re_codigo: int) -> bool:
        """
        Verifica si una persona ya pertenece a un grupo que está registrado para un retorno específico.
        """
        stmt = (
            select(persona_grupo_retorno)
            .join(RegistroRetornoGrupo, persona_grupo_retorno.gr_codigo == RegistroRetornoGrupo.cod_grupo)
            .where(
                persona_grupo_retorno.pe_codigo == pe_codigo,
                RegistroRetornoGrupo.retorno == re_codigo
            )
        )
        result = await self.db.execute(stmt)
        return result.scalars().first() is not None