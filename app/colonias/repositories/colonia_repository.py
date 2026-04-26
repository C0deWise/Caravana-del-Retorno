"""
Modulo que gestiona el acceso de datos para la entidad Colonia.
Contiene las operaciones de consulta e inserción en la base de datos
relacionadas con colonias colombianas, utilizando sesiones SQLAlchemy
como capa de persistencia.
"""

from app.usuarios.models import usuario
from app.usuarios.models.usuario import Usuario
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.colonias.models.colonia_model import Colonia, ColoniaEstado
from app.colonias.schemas.colonia_schemas import ColoniaCrear

class ColoniaRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def crear_colonia(self, datos: ColoniaCrear) -> Colonia:
        """
        Inserta una nueva colonia en la base de datos.
        Parámetros:
            db (AsyncSession): Sesión activa de SQLAlchemy.
            datos (ColoniaCrear): Datos validados de la colonia a crear.
        Retorna:
            Colonia: Objeto de la colonia recién creado con su id generado.
        """
        colonia = Colonia(
            pais=datos.pais,
            departamento=datos.departamento,
            ciudad=datos.ciudad,
            lider=datos.lider,
        )
        self.db.add(colonia)
        await self.db.commit()
        await self.db.refresh(colonia)
        return colonia

    async def obtener_colonia_por_ubicacion(
        self, pais: str, departamento: str, ciudad: str
    ) -> Colonia | None:
        """
        Busca una colonia existente por su ubicación exacta.
        Parámetros:
            db (AsyncSession): Sesion activa de SQLAlchemy.
            pais (str): País de la colonia.
            departamento (str): Departamento de la colonia.
            ciudad (str): Ciudad de la colonia.
        Retorna:
            Colonia | None: La colonia encontrada o None si no existe.
        """
        sentencia = select(Colonia).filter(
            Colonia.pais == pais,
            Colonia.departamento == departamento,
            Colonia.ciudad == ciudad
        )
        resultado = await self.db.execute(sentencia)
        return resultado.scalars().first()
    
    async def obtener_colonia_por_id(self, colonia_codigo: int) -> Colonia | None:
        sentencia = select(Colonia).filter(Colonia.codigo == colonia_codigo)
        resultado = await self.db.execute(sentencia)
        return resultado.scalars().first()

    async def establecer_lider_colonia(self, colonia_codigo: int, lider_id: int) -> Colonia:
        colonia = await self.obtener_colonia_por_id(colonia_codigo)
        colonia.lider = lider_id
        usuario = await self.db.get(Usuario, lider_id)
        usuario.ro_codigo = 2 #Cambia rol a líder

        if usuario.co_codigo is None:
            usuario.co_codigo = colonia_codigo

        await self.db.commit()
        await self.db.refresh(colonia)
        return colonia
      
    async def obtener_colonias(self) -> list[Colonia]:
        sentencia = select(Colonia)
        resultado = await self.db.execute(sentencia)
        return resultado.scalars().all()
    
    async def tiene_miembros_colonia(self, colonia_codigo: int) -> bool:
        sentencia = select(Usuario).filter(Usuario.co_codigo == colonia_codigo)
        resultado = await self.db.execute(sentencia)
        if resultado.scalars().first():
            return True
        else:
            return False
        
    async def sacar_miembros_colonia(self, colonia_codigo: int) -> list[Usuario]:
        sentencia = select(Usuario).filter(Usuario.co_codigo == colonia_codigo)
        resultado = await self.db.execute(sentencia)
        usuarios = resultado.scalars().all()

        usuarios_desasociados = []
        for usuario in usuarios:
            usuarios_desasociados.append(usuario)
            usuario.co_codigo = None

            if usuario.ro_codigo == 2:
                usuario.ro_codigo = 1 #Cambia rol a usuario común

            await self.db.commit()
            await self.db.refresh(usuario)
        
        return usuarios_desasociados

    async def desactivar_colonia(self, colonia: Colonia) -> Colonia:
        colonia.estado = ColoniaEstado.INACTIVA
        colonia.lider = None
        await self.db.commit()
        await self.db.refresh(colonia)
        return colonia

    async def cambiar_lider_colonia(self, colonia_codigo: int, nuevo_lider_id: int) -> Colonia:
        colonia = await self.obtener_colonia_por_id(colonia_codigo)
        usuario_antiguo = await self.db.get(Usuario, colonia.lider)
        usuario_antiguo.ro_codigo = 1
        usuario_nuevo = await self.db.get(Usuario, nuevo_lider_id)
        usuario_nuevo.ro_codigo = 2
        colonia.lider = nuevo_lider_id
        await self.db.commit()
        await self.db.refresh(colonia)
        return colonia
