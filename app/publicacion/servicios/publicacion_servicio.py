"""
Modulo de servicios para la gestión de publicaciones en la aplicación. Contiene la clase PublicacionServicio,
que implementa la lógica de negocio para crear nuevas publicaciones, consultar publicaciones por retorno y por
código, y manejar la asociación de archivos multimedia a las publicaciones. Este servicio interactúa con los repositorios
correspondientes para acceder a la base de datos y con otros servicios para validar la existencia de retornos y usuarios,
así como para gestionar los archivos multimedia asociados a las publicaciones.
"""

from fastapi import UploadFile

from app.publicacion.esquemas.publicacion_esquema import PublicacionCrear, PublicacionRespuesta
from app.publicacion.repositorios.publicacion_repositorio import PublicacionRepositorio
from app.multimedia.servicios.multimedia_servicio import MultimediaServicio
from app.retornos.servicios.retorno_servicio import RetornoService
from app.publicacion.excepciones.publicacion_excepciones import PublicacionNoExistenteError, RetornoNoExistenteError, UsuarioNoExistenteError
from app.usuarios.services.usuario_servicio import UsuarioServicio

class PublicacionServicio:
    def __init__(self, repositorio: PublicacionRepositorio, multimedia_servicio: MultimediaServicio = None, retorno_servicio: RetornoService = None, usuario_servicio: UsuarioServicio = None):
        self.repositorio = repositorio
        self.multimedia_servicio = multimedia_servicio
        self.retorno_servicio = retorno_servicio
        self.usuario_servicio = usuario_servicio

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
        retorno = await self.retorno_servicio.obtener_retorno(datos.retorno)
        if not retorno:
            raise RetornoNoExistenteError(datos.retorno)
        
        usuario = await self.usuario_servicio.obtener_usuario_por_id(datos.autor)
        if not usuario:
            raise UsuarioNoExistenteError(datos.autor)
        
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
        publicacion = await self.repositorio.consultar_publicacion_por_codigo(codigo)
        if not publicacion:
            raise PublicacionNoExistenteError(codigo)
        return PublicacionRespuesta.model_validate(publicacion, from_attributes=True)