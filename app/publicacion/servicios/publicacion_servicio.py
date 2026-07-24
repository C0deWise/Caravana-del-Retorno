"""
Modulo de servicios para la gestión de publicaciones en la aplicación. Contiene la clase PublicacionServicio,
que implementa la lógica de negocio para crear nuevas publicaciones, consultar publicaciones por retorno y por
código, y manejar la asociación de archivos multimedia a las publicaciones. Este servicio interactúa con los repositorios
correspondientes para acceder a la base de datos y con otros servicios para validar la existencia de retornos y usuarios,
así como para gestionar los archivos multimedia asociados a las publicaciones.
"""

from fastapi import UploadFile

from app.publicacion.esquemas.publicacion_esquema import PublicacionCrear, PublicacionRespuesta, PublicacionEditar
from app.publicacion.repositorios.publicacion_repositorio import PublicacionRepositorio
from app.multimedia.servicios.multimedia_servicio import MultimediaServicio
from app.retornos.servicios.retorno_servicio import RetornoService
from app.publicacion.excepciones.publicacion_excepciones import PublicacionNoExistenteError, RetornoNoExistenteError, UsuarioNoExistenteError
from app.usuarios.services.usuario_servicio import UsuarioServicio

import logging
logger = logging.getLogger(__name__)
class PublicacionServicio:
    def __init__(self, repositorio: PublicacionRepositorio, multimedia_servicio: MultimediaServicio, retorno_servicio: RetornoService, usuario_servicio: UsuarioServicio):
        self.repositorio = repositorio
        self.multimedia_servicio = multimedia_servicio
        self.retorno_servicio = retorno_servicio
        self.usuario_servicio = usuario_servicio

    async def _validar_retorno(self, retorno_id: int):
        """Valida la existencia de un retorno específico."""
        retorno = await self.retorno_servicio.obtener_retorno(retorno_id)
        if not retorno:
            raise RetornoNoExistenteError(retorno_id)
        return retorno

    async def _validar_usuario(self, usuario_id: int):
        """Valida la existencia de un usuario específico."""
        usuario = await self.usuario_servicio.obtener_usuario_por_id(usuario_id)
        if not usuario:
            raise UsuarioNoExistenteError(usuario_id)
        return usuario
    
    async def _validar_publicacion(self, codigo: int):
        """Valida la existencia de una publicación específica."""
        publicacion = await self.repositorio.consultar_publicacion_por_codigo(codigo)
        if not publicacion:
            raise PublicacionNoExistenteError(codigo)
        return publicacion

    async def crear_publicacion(self, datos: PublicacionCrear, archivos: list[UploadFile]) -> PublicacionRespuesta:
        """
        Crea una nueva publicación, validando la existencia del retorno y del usuario autor. Si se proporcionan
        archivos multimedia, se asocian a la publicación creada. Devuelve la publicación completa con todos sus 
        datos y archivos multimedia asociados.
        Args:
            datos (PublicacionCrear): Esquema con los datos necesarios para crear la publicación.
            archivos (list[UploadFile]): Lista de archivos multimedia a asociar a la publicación.
        Returns:
            PublicacionRespuesta: Esquema con los datos de la publicación creada, incluyendo los archivos multimedia asociados.
        Raises:
            RetornoNoExistenteError: Si el retorno especificado no existe.
            UsuarioNoExistenteError: Si el usuario autor especificado no existe.
        """
        await self._validar_retorno(datos.retorno)
        await self._validar_usuario(datos.autor)
        
        nueva_publicacion = await self.repositorio.crear_publicacion(datos)
        print(f"Publicación creada: {nueva_publicacion}, datos: {datos}, archivos: {archivos}")

        if archivos:
            await self.multimedia_servicio.cargar_archivos_multimedia(nueva_publicacion.codigo, datos.retorno, archivos)

        publicacion_completa = await self.repositorio.consultar_publicacion_por_codigo(nueva_publicacion.codigo)

        return PublicacionRespuesta.model_validate(publicacion_completa, from_attributes=True)
    
    async def consultar_publicacion_por_retorno(self, retorno_id: int) -> list[PublicacionRespuesta]:
        """
        Consulta las publicaciones asociadas a un retorno específico. Devuelve una lista de publicaciones con sus datos
        completos, incluyendo los archivos multimedia asociados a cada publicación.
        Args:
            retorno_id (int): ID del retorno para el cual se desean consultar las publicaciones.
        Returns:
            list[PublicacionRespuesta]: Lista de publicaciones asociadas al retorno, con sus datos completos y archivos
            multimedia.
        """
        publicaciones = await self.repositorio.consultar_publicaciones_por_retorno(retorno_id)
        print(f"Publicaciones obtenidas para retorno {retorno_id}: {publicaciones}")
        return [PublicacionRespuesta.model_validate(p, from_attributes=True) for p in publicaciones]
    
    async def consultar_publicacion_por_codigo(self, codigo: int) -> PublicacionRespuesta:
        """
        Consulta una publicación específica por su código. Devuelve la publicación con sus datos completos, incluyendo los
        archivos multimedia asociados.
        Args:
            codigo (int): Código de la publicación a consultar.
        Returns:
            PublicacionRespuesta: Esquema con los datos de la publicación consultada, incluyendo los archivos multimedia 
            asociados.
        Raises:
            PublicacionNoExistenteError: Si no existe una publicación con el código especificado.
        """
        publicacion = await self._validar_publicacion(codigo)

        return PublicacionRespuesta.model_validate(publicacion, from_attributes=True)
    
    async def editar_publicacion(self, codigo: int, datos: PublicacionEditar, archivos_nuevos: list[UploadFile] | None = None) -> PublicacionRespuesta:
        """
        Edita una publicación existente. Valida la existencia del retorno y del usuario autor antes de realizar la edición.
        Devuelve la publicación editada con sus datos completos.
        Args:
            codigo (int): Código de la publicación a editar.
            datos (PublicacionCrear): Esquema con los nuevos datos para la publicación.
        Returns:
            PublicacionRespuesta: Esquema con los datos de la publicación editada, incluyendo los archivos multimedia asociados.
        Raises:
            RetornoNoExistenteError: Si el retorno especificado no existe.
            UsuarioNoExistenteError: Si el usuario autor especificado no existe.
            PublicacionNoExistenteError: Si no existe una publicación con el código especificado.
        """
        await self._validar_retorno(datos.retorno)
        await self._validar_usuario(datos.autor)
        await self._validar_publicacion(codigo)

        if datos.archivos_eliminar:
            await self.multimedia_servicio.eliminar_archivos_multimedia(codigo, datos.archivos_eliminar)

        if archivos_nuevos:
            await self.multimedia_servicio.cargar_archivos_multimedia(codigo, datos.retorno, archivos_nuevos)

        publicacion_editada = await self.repositorio.editar_publicacion(codigo, datos)

        logger.info(f"Publicación editada: {publicacion_editada}, datos: {datos}, archivos nuevos: {archivos_nuevos}")
        return PublicacionRespuesta.model_validate(publicacion_editada, from_attributes=True)