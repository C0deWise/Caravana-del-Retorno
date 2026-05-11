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
        publicaciones = await self.repositorio.consultar_publicaciones_por_retorno(retorno_id)
        print(f"Publicaciones obtenidas para retorno {retorno_id}: {publicaciones}")
        return [PublicacionRespuesta.model_validate(p, from_attributes=True) for p in publicaciones]
    
    async def consultar_publicacion_por_codigo(self, codigo: int) -> PublicacionRespuesta:
        publicacion = await self.repositorio.consultar_publicacion_por_codigo(codigo)
        if not publicacion:
            raise PublicacionNoExistenteError(codigo)
        return PublicacionRespuesta.model_validate(publicacion, from_attributes=True)