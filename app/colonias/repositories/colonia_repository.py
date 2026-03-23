"""
Modulo que gestiona el acceso de datos para la entidad Colonia.
Contiene las operaciones de consulta e inserción en la base de datos
relacionadas con colonias colombianas, utilizando sesiones SQLAlchemy
como capa de persistencia.
"""

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
