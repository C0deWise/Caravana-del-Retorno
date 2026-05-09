import aiofiles
from fastapi import UploadFile
from pathlib import Path

from app.multimedia.modelos.multimedia_modelo import Multimedia
from app.multimedia.esquemas.multimedia_esquemas import MultimediaCrear, MultimediaRespuesta
from app.multimedia.repositorios.multimedia_repositorio import MultimediaRepositorio
from app.retornos.servicios.retorno_servicio import RetornoService
from app.multimedia.excepciones.multimedia_excepciones import RetornoNoExistenteError, TipoArchivoNoValidoError
from app.multimedia.config import TipoMultimedia, EXTENSIONES_POR_TIPO

class MultimediaServicio:
    def __init__(self, repositorio: MultimediaRepositorio, retorno_servicio: RetornoService = None):
        self.repositorio = repositorio
        self.retorno_servicio = retorno_servicio

    def validar_archivo(self, nombre_archivo: str) -> str:
        extension = Path(nombre_archivo).suffix.lower()

        for tipo, extensiones in EXTENSIONES_POR_TIPO.items():
            if extension in extensiones:
                return tipo.value
        raise TipoArchivoNoValidoError()
        
    async def guardar_archivo_local(self, archivo: UploadFile, retorno_codigo: int) -> str:

        upload_dir = Path(f"/app/multimedia/retorno_{retorno_codigo}")
        upload_dir.mkdir(parents=True, exist_ok=True)

        ruta_archivo = upload_dir / archivo.filename

        async with aiofiles.open(ruta_archivo, 'wb') as buffer:
            content = await archivo.read()
            await buffer.write(content)

        return str(ruta_archivo)
    
    async def cargar_archivos_multimedia(self, retorno_codigo: int, archivos: list[UploadFile]) -> list[MultimediaRespuesta]:

        retorno = await self.retorno_servicio.obtener_retorno(retorno_codigo)
        if not retorno:
            raise RetornoNoExistenteError(retorno_codigo)
        
        resultados = []

        for archivo in archivos:
            tipo = self.validar_archivo(archivo.filename)
            ruta_guardada = await self.guardar_archivo_local(archivo, retorno_codigo)

            multimedia_data = MultimediaCrear(
                retorno=retorno_codigo,
                tipo=tipo,
                url=ruta_guardada,
                nombre_archivo=archivo.filename
            )
            multimedia = await self.repositorio.crear_multimedia(multimedia_data)
            resultados.append(multimedia)
        
        return [MultimediaRespuesta.model_validate(m, from_attributes=True) for m in resultados]

    async def obtener_multimedia_por_retorno(self, retorno_codigo: int) -> list[MultimediaRespuesta]:
        retorno = await self.retorno_servicio.obtener_retorno(retorno_codigo)
        if not retorno:
            raise RetornoNoExistenteError(retorno_codigo)

        multimedia_list = await self.repositorio.obtener_multimedia_por_retorno(retorno_codigo)
        return [MultimediaRespuesta.model_validate(m, from_attributes=True) for m in multimedia_list]
