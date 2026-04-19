"""
Módulo que contiene la lógica de negocio para la entidad Colonia.
Coordina la validación de reglas de negocio y la interacción con el
repositorio de colonias, garantizando la integridad de los datos antes 
de su persistencia en la base de datos.
"""
from app.colonias.excepciones.excepciones import ColoniaInactiva, ColoniaNoExistente
from app.colonias.models.colonia_model import ColoniaEstado
from sqlalchemy.ext.asyncio import AsyncSession
from app.colonias.schemas.colonia_schemas import ColoniaCrear, ColoniaRespuesta
from app.colonias.repositories.colonia_repository import ColoniaRepository
from app.usuarios.repository.usuario_repositorio import UsuarioRepositorio
from app.usuarios.services.usuario_servicio import UsuarioServicio

from fastapi import HTTPException, status

class ColoniaService:

    def __init__(self, repositorio: ColoniaRepository, db: AsyncSession):
        self.repositorio = repositorio
        self.usuario_servicio = UsuarioServicio(UsuarioRepositorio(db))

    async def servicio_crear_colonia(self, datos: ColoniaCrear) -> ColoniaRespuesta:
        """
        Crear una nueva colonia aplicando reglas de negocio.
        Parámetros:
            db (AsyncSession): Sesión activa de SQLAlchemy.
            datos (ColoniaCrear): Datos validados de la colonia a crear.
        Retorna:
            ColoniaRespuesta: Datos de la colonia creada.
        Excepciones:
            HTTPException 409: Si ya existe una colonia con la misma ubicación.
        """
        #Verificar si ya existe una colonia con la misma ubicación.
        colonia_existente = await self.repositorio.obtener_colonia_por_ubicacion(
            pais=datos.pais,
            departamento=datos.departamento,
            ciudad=datos.ciudad,
        )

        if colonia_existente and (not datos.departamento or not datos.ciudad): 
            raise HTTPException (
                status_code = status.HTTP_409_CONFLICT,
                detail=f"Ya existe una colonia en {datos.pais}.",
                )
        elif colonia_existente:
            raise HTTPException (
                status_code = status.HTTP_409_CONFLICT,
                detail=f"Ya existe una colonia en {datos.ciudad}, {datos.departamento}, {datos.pais}.",
                )

        #Crear la colonia sino existe duplicado
        nueva_colonia = await self.repositorio.crear_colonia(datos)
        return ColoniaRespuesta.model_validate(nueva_colonia, from_attributes=True)
    
    async def servicio_establecer_lider(self, colonia_codigo: int, lider_id: int) -> ColoniaRespuesta:
        """
            Asigna un líder a una colonia existente.
            Parámetros:
                db (Session): Sesión activa de SQLAlchemy.
                colonia_codigo (int): Código de la colonia a actualizar.
                lider_id (int): ID del líder a asignar.
            Retorna:
                ColoniaRespuesta: La colonia actualizada con el nuevo líder.
            Excepciones:
                HTTPException 404: Si la colonia no existe en la base de datos.
        """
        colonia = await self.repositorio.obtener_colonia_por_id(colonia_codigo)
        if not colonia:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Colonia con código {colonia_codigo} no encontrada")
        
        usuario_lider = await self.usuario_servicio.obtener_usuario_por_id(lider_id)
        if not usuario_lider:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Usuario con ID {lider_id} no encontrado")
        
        if colonia.lider != 0:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail=f"La colonia con código {colonia_codigo} ya tiene un líder asignado")

        colonia_actualizada = await self.repositorio.establecer_lider_colonia(colonia_codigo, lider_id)
        return ColoniaRespuesta.model_validate(colonia_actualizada, from_attributes=True)
    
    async def obtener_colonias(self) -> list[ColoniaRespuesta]:
        colonias = await self.repositorio.obtener_colonias()
        return [ColoniaRespuesta.model_validate(colonia, from_attributes=True) for colonia in colonias]
    
    async def desactivar_colonia(self, colonia_codigo: int) -> ColoniaRespuesta:
        colonia = await self.repositorio.obtener_colonia_por_id(colonia_codigo)
        if not colonia:
            raise ColoniaNoExistente(colonia_codigo)
        
        if colonia.estado == ColoniaEstado.INACTIVA:
            raise ColoniaInactiva(colonia_codigo)
         
        tiene_miembros = await self.repositorio.tiene_miembros_colonia(colonia_codigo)
        if tiene_miembros:
            #Desasociar miembros de la colonia antes de desactivarla, incluye el cambio de rol de líder a usuario común
            await self.repositorio.sacar_miembros_colonia(colonia_codigo)
        
        colonia_desactivada = await self.repositorio.desactivar_colonia(colonia)
        return ColoniaRespuesta.model_validate(colonia_desactivada, from_attributes=True)
