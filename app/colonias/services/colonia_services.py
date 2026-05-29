"""
Módulo que contiene la lógica de negocio para la entidad Colonia.
Coordina la validación de reglas de negocio y la interacción con el
repositorio de colonias, garantizando la integridad de los datos antes 
de su persistencia en la base de datos.
"""
from app.colonias.excepciones.excepciones import ColoniaInactiva, ColoniaNoExistente, UsuarioYaTieneColonia
from app.colonias.models.colonia_model import ColoniaEstado
from sqlalchemy.ext.asyncio import AsyncSession
from app.colonias.excepciones.excepciones import (
AutoRemocionUsuarioColonia,
ColoniaInactiva, 
ColoniaNoExistente,
ColoniaSinLiderAsignado,
UsuarioNoExistente, 
UsuarioYaEsLider,
UsuarioNoEsMiembroColonia,
UsuarioInscritoRetornoActivo)
from app.colonias.models.colonia_model import ColoniaEstado
from app.colonias.schemas.colonia_schemas import ColoniaCrear, ColoniaRespuesta, UsuarioRemovidoColonia, UsuarioRemovidoColoniaRespuesta
from app.colonias.repositories.colonia_repository import ColoniaRepository
from app.usuarios.services.usuario_servicio import UsuarioServicio
from app.retornos.servicios.registro_retorno_servicio import RegistroRetornoServicio

from fastapi import HTTPException, status

class ColoniaService:

    def __init__(self, repositorio: ColoniaRepository, usuario_servicio: UsuarioServicio = None, registro_retorno_servicio: RegistroRetornoServicio = None):
        self.repositorio = repositorio
        self.usuario_servicio = usuario_servicio
        self.registro_retorno_servicio = registro_retorno_servicio

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
        if colonia.estado == ColoniaEstado.INACTIVA:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail=f"La colonia con código {colonia_codigo} está inactiva")
        usuario_lider = await self.usuario_servicio.obtener_usuario_por_id(lider_id)
        if not usuario_lider:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Usuario con ID {lider_id} no encontrado")
        
        if colonia.lider is not None:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail=f"La colonia con código {colonia_codigo} ya tiene un líder asignado")

        colonia_actualizada = await self.repositorio.establecer_lider_colonia(colonia_codigo, lider_id)
        return ColoniaRespuesta.model_validate(colonia_actualizada, from_attributes=True)
    
    async def obtener_colonias(self) -> list[ColoniaRespuesta]:
        """
        Obtiene la lista de colonias existentes.
        Parámetros:
            db (Session): Sesión activa de SQLAlchemy.
        Retorna:
            list[ColoniaRespuesta]: Lista de colonias existentes.
        """
        colonias = await self.repositorio.obtener_colonias()
        return [ColoniaRespuesta.model_validate(colonia, from_attributes=True) for colonia in colonias]
    
    async def obtener_colonia(self, colonia_codigo: int) -> ColoniaRespuesta:
        colonia = await self.repositorio.obtener_colonia_por_id(colonia_codigo)
        if not colonia:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Colonia con código {colonia_codigo} no encontrada")
        return ColoniaRespuesta.model_validate(colonia, from_attributes=True)
    
    async def toggle_estado_colonia(self, colonia_codigo: int) -> ColoniaRespuesta:
        """
        Alterna el estado de una colonia existente. Si una colonia tiene miembros, se desasocian los miembros
        antes de alterar el estado de la colonia, incluye el cambio de rol a usuario l+ider a usuario común.
        Parámetros:
            colonia_codigo (int): Código de la colonia a desactivar o activar.
        Retorna:
            ColoniaRespuesta: La colonia desactivada o activada.
        Excepciones:
            HTTPException 404: Si la colonia no existe en la base de datos.
        """
        colonia = await self.repositorio.obtener_colonia_por_id(colonia_codigo)
        if not colonia:
            raise ColoniaNoExistente(colonia_codigo)
        
        if colonia.estado == ColoniaEstado.INACTIVA:
            return await self.repositorio.activar_colonia(colonia.codigo)
         
        tiene_miembros = await self.repositorio.tiene_miembros_colonia(colonia_codigo)
        if tiene_miembros:
            #Desasociar miembros de la colonia antes de desactivarla, incluye el cambio de rol de líder a usuario común
            await self.repositorio.sacar_miembros_colonia(colonia_codigo)
        
        colonia_desactivada = await self.repositorio.desactivar_colonia(colonia)
        return ColoniaRespuesta.model_validate(colonia_desactivada, from_attributes=True)
      
    async def obtener_colonias_activas(self) -> list[ColoniaRespuesta]:
        """
        Obtiene la lista de colonias activas.
        Parámetros:
            db (Session): Sesión activa de SQLAlchemy.
        Retorna:
            list[ColoniaRespuesta]: Lista de colonias activas.
        """
        colonias_activas = await self.repositorio.obtener_colonias_activas()
        return [ColoniaRespuesta.model_validate(colonia, from_attributes=True) for colonia in colonias_activas]
      
    async def cambiar_lider_colonia(self, colonia_codigo: int, nuevo_lider_id: int) -> ColoniaRespuesta:
        """
        Cambia el líder de una colonia existente. Verifica que la colonia exista, tenga un líder asignado previamente,
        que el nuevo líder exista, sea miembro de la colonia y sea diferente al líder actual antes de realizar el cambio.
        Parámetros:
            colonia_codigo (int): Código de la colonia a actualizar.
            nuevo_lider_id (int): ID del nuevo líder a asignar.
        Retorna:
            ColoniaRespuesta: La colonia actualizada con el nuevo líder.
        Excepciones:
            HTTPException 404: Si la colonia o el nuevo líder no existen en la base de datos.
            HTTPException 409: Si la colonia no tiene un líder asignado, el nuevo líder no es 
                            miembro de la colonia o ya es el líder actual.
        """
        
        colonia = await self.repositorio.obtener_colonia_por_id(colonia_codigo)
        if not colonia:
            raise ColoniaNoExistente(colonia_codigo)
        if colonia.estado == ColoniaEstado.INACTIVA:
            raise ColoniaInactiva(colonia_codigo)
        if colonia.lider is None:
            raise ColoniaSinLiderAsignado(colonia_codigo)
        
        usuario_nuevo_lider = await self.usuario_servicio.obtener_usuario_por_id(nuevo_lider_id)
        if not usuario_nuevo_lider:
            raise UsuarioNoExistente(nuevo_lider_id)
        
        if usuario_nuevo_lider.co_codigo is not None and usuario_nuevo_lider.co_codigo != colonia_codigo:
            raise UsuarioYaTieneColonia(usuario_nuevo_lider.us_codigo, usuario_nuevo_lider.co_codigo, colonia_codigo)
        
        if colonia.lider == nuevo_lider_id:
            raise UsuarioYaEsLider(nuevo_lider_id, colonia_codigo)

        colonia_actualizada = await self.repositorio.cambiar_lider_colonia(colonia_codigo, nuevo_lider_id)
        return ColoniaRespuesta.model_validate(colonia_actualizada, from_attributes=True)

    async def remover_miembro_colonia(self, colonia_id: int, usuario_id: int) -> UsuarioRemovidoColoniaRespuesta:
        """
        Remueve a un miembro específico de una colonia, teniendo en cuenta que el usuario exista, pertenezca a
        una colonia y no este inscrito a un retorno activo. Para el rol de líder no se puede remover a sí mismo, 
        se debe cambiar el líder primero para luego removerlo como miembro.
        Parámetros:
            colonia_id (int): El código de la colonia de la cual se desea remover al usuario.
            usuario_id (int): El ID del usuario que se desea remover de la colonia.
        Retorna:
            UsuarioRemovidoColoniaRespuesta: Un mensaje de confirmación junto con los datos del usuario removido.
        Excepciones:
            ColoniaNoExistente: Si la colonia con el ID proporcionado no existe.
            UsuarioNoExistente: Si el usuario con el ID proporcionado no existe.
            UsuarioNoEsMiembroColonia: Si el usuario no es miembro de la colonia especificada.
            AutoRemocionUsuarioColonia: Si el usuario a remover es el líder de la colonia.
            UsuarioInscritoRetornoActivo: Si el usuario tiene registros de retorno activos.
        """
        usuario = await self.usuario_servicio.obtener_usuario_por_id(usuario_id)
        if not usuario:
            raise UsuarioNoExistente(usuario_id)
        
        colonia = await self.repositorio.obtener_colonia_por_id(colonia_id)
        if not colonia:
            raise ColoniaNoExistente(colonia_id)

        if usuario.co_codigo != colonia_id:
            raise UsuarioNoEsMiembroColonia(usuario_id, colonia_id)
        
        if colonia.lider == usuario_id:
            raise AutoRemocionUsuarioColonia(usuario_id)
        
        registros_retorno_usuario = await self.registro_retorno_servicio.obtener_registros_retorno_activos_por_usuario(usuario_id)
        if registros_retorno_usuario:
            raise UsuarioInscritoRetornoActivo(usuario_id)

        usuario_removido = await self.repositorio.remover_miembro_colonia(usuario)

        usuario_removido_esquema = UsuarioRemovidoColonia.model_validate(usuario_removido, from_attributes=True)
        
        return UsuarioRemovidoColoniaRespuesta(
            mensaje=f"El usuario {usuario_removido_esquema.nombre} {usuario_removido_esquema.apellido} ha sido removido exitosamente de la colonia.",
            usuario=usuario_removido_esquema
        )
