"""
Modulo que gestiona el acceso de datos para la entidad Colonia.
Contiene las operaciones de consulta e inserción en la base de datos
relacionadas con colonias colombianas, utilizando sesiones SQLAlchemy
como capa de persistencia.
"""

from app.usuarios.models.usuario import Usuario
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.colonias.models.colonia_model import Colonia
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
            co_pais=datos.pais,
            co_departamento=datos.departamento,
            co_ciudad=datos.ciudad,
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
            Colonia.co_pais == pais,
            Colonia.co_departamento == departamento,
            Colonia.co_ciudad == ciudad
        )
        resultado = await self.db.execute(sentencia)
        return resultado.scalars().first()
    
    async def obtener_colonia_por_id(self, colonia_codigo: int) -> Colonia | None:
        sentencia = select(Colonia).filter(Colonia.co_codigo == colonia_codigo)
        resultado = await self.db.execute(sentencia)
        return resultado.scalars().first()

    async def establecer_lider_colonia(self, colonia_codigo: int, lider_id: int) -> Colonia:
        """
        Establece un líder para una colonia existente.
        Parámetros:
            db (AsyncSession): Sesión activa de SQLAlchemy.
            colonia_codigo (int): Código de la colonia a actualizar.
            lider_id (int): ID del líder a asignar.
        Retorna:
            Colonia: La colonia actualizada con el nuevo líder.
        """
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
        """
        Obtiene todas las colonias existentes en la base de datos.
        Parámetros:
            db (AsyncSession): Sesión activa de SQLAlchemy.
        Retorna:
            list[Colonia]: Lista de objetos Colonia existentes.
        """
        sentencia = select(Colonia)
        resultado = await self.db.execute(sentencia)
        return resultado.scalars().all()
    
    async def tiene_miembros_colonia(self, colonia_codigo: int) -> bool:
        """
        Verifica si una colonia tiene miembros asociados. Identificando si el usuario 
        tiene el número de colonia igual al código de la colonia.
        Parámetros:
            db (AsyncSession): Sesión activa de SQLAlchemy.
            colonia_codigo (int): Código de la colonia a verificar.
        Retorna:
            bool: True si la colonia tiene miembros asociados, False en caso contrario.
        """
        sentencia = select(Usuario).filter(Usuario.co_codigo == colonia_codigo)
        resultado = await self.db.execute(sentencia)
        if resultado.scalars().first():
            return True
        else:
            return False
        
    async def sacar_miembros_colonia(self, colonia_codigo: int) -> list[Usuario]:
        """
        Desasocia todos los miembros de una colonia, estableciendo su co_codigo a None 
        y cambiando su rol a usuario común si es necesario.
        Parámetros:
            db (AsyncSession): Sesión activa de SQLAlchemy.
            colonia_codigo (int): Código de la colonia de la cual desasociar miembros.
        Retorna:
            list[Usuario]: Lista de usuarios desasociados.
        """
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
        """
        Desactiva una colonia existente, estableciendo su estado a inactiva y su líder a None.
        Parámetros:
            db (AsyncSession): Sesión activa de SQLAlchemy.
            colonia (Colonia): La colonia a desactivar.
        Retorna:
             Colonia: La colonia desactivada.
        """
        colonia.estado = ColoniaEstado.INACTIVA
        colonia.lider = None
        await self.db.commit()
        await self.db.refresh(colonia)
        return colonia
        
