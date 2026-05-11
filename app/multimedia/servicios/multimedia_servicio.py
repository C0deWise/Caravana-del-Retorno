import aiofiles
from fastapi import UploadFile
from pathlib import Path

from app.multimedia.esquemas.multimedia_esquemas import MultimediaCrear, MultimediaRespuesta
from app.multimedia.repositorios.multimedia_repositorio import MultimediaRepositorio
from app.multimedia.excepciones.multimedia_excepciones import TipoArchivoNoValidoError
from app.multimedia.config import EXTENSIONES_POR_TIPO

class MultimediaServicio:
    def __init__(self, repositorio: MultimediaRepositorio):
        self.repositorio = repositorio

    def validar_archivo(self, nombre_archivo: str) -> tuple[str, str]:
        extension = Path(nombre_archivo).suffix.lower()

        for tipo_formato, extensiones in EXTENSIONES_POR_TIPO.items():
            if extension in extensiones:
                tipo, formato = tipo_formato
                print(f"Archivo '{nombre_archivo}' identificado como tipo '{tipo.value}' y formato '{formato.value}'")
                return tipo, formato
                
        raise TipoArchivoNoValidoError()
        
    async def guardar_archivo_local(self, archivo: UploadFile, retorno_codigo: int) -> str:

        upload_dir = Path(f"/app/multimedia/retorno_{retorno_codigo}")
        upload_dir.mkdir(parents=True, exist_ok=True)

        ruta_archivo = upload_dir / archivo.filename
        print(f"Guardando archivo '{archivo.filename}' en '{ruta_archivo}'")

        async with aiofiles.open(ruta_archivo, 'wb') as buffer:
            content = await archivo.read()
            await buffer.write(content)

        return str(ruta_archivo)
    
    async def cargar_archivos_multimedia(self, publicacion_id: int, retorno_codigo: int, archivos: list[UploadFile]) -> list[MultimediaRespuesta]:
        
        resultados = []

        for archivo in archivos:
            tipo, formato = self.validar_archivo(archivo.filename)
            ruta_guardada = await self.guardar_archivo_local(archivo, retorno_codigo)
            print(f"Archivo '{archivo.filename}' guardado en '{ruta_guardada}'")

            multimedia_data = MultimediaCrear(
                publicacion=publicacion_id,
                tipo=tipo,
                formato=formato,
                url=ruta_guardada,
                descripcion=archivo.filename
            )

            print(f"Creando entrada de multimedia en base de datos con datos: {multimedia_data}")

            multimedia = await self.repositorio.crear_multimedia(multimedia_data)
            print(f"Multimedia creado en base de datos: {multimedia}")
            resultados.append(multimedia)
        
        return [MultimediaRespuesta.model_validate(m, from_attributes=True) for m in resultados]

    async def obtener_multimedia_por_retorno(self, publicacion_id: int) -> list[MultimediaRespuesta]:
        multimedia_list = await self.repositorio.obtener_multimedia_por_retorno(publicacion_id)
        return [MultimediaRespuesta.model_validate(m, from_attributes=True) for m in multimedia_list]
