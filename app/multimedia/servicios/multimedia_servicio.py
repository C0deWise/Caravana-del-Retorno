"""
Modulo de servicio para la gestión de multimedia en la aplicación. Este módulo se encarga de validar, 
almacenar y recuperar archivos multimedia asociados a publicaciones. Proporciona funcionalidades para 
cargar archivos, identificar su tipo y formato, y gestionar su almacenamiento local. Además, interactúa 
con el repositorio de multimedia para persistir la información en la base de datos y recuperar los datos 
necesarios para las respuestas de la API.  
"""

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
        """
        Valida el tipo y formato del archivo basado en su extensión.
        Args:
            nombre_archivo (str): El nombre del archivo a validar.
        Returns:
            tuple[str, str]: Una tupla con el tipo y formato del archivo.
        """
        extension = Path(nombre_archivo).suffix.lower()

        for tipo_formato, extensiones in EXTENSIONES_POR_TIPO.items():
            if extension in extensiones:
                tipo, formato = tipo_formato
                print(f"Archivo '{nombre_archivo}' identificado como tipo '{tipo.value}' y formato '{formato.value}'")
                return tipo, formato
                
        raise TipoArchivoNoValidoError()
        
    async def guardar_archivo_local(self, archivo: UploadFile, retorno_codigo: int) -> str:
        """
        Guarda un archivo multimedia localmente en el sistema de archivos.
        Args:
            archivo (UploadFile): El archivo a guardar.
            retorno_codigo (int): El código del retorno asociado al archivo.
        Returns:
            str: La ruta donde se guardó el archivo.
        """
        upload_dir = Path(f"/app/multimedia/retorno_{retorno_codigo}")
        upload_dir.mkdir(parents=True, exist_ok=True)

        ruta_archivo = upload_dir / archivo.filename
        print(f"Guardando archivo '{archivo.filename}' en '{ruta_archivo}'")

        async with aiofiles.open(ruta_archivo, 'wb') as buffer:
            content = await archivo.read()
            await buffer.write(content)

        return str(ruta_archivo)
    
    async def cargar_archivos_multimedia(self, publicacion_id: int, retorno_codigo: int, archivos: list[UploadFile]) -> list[MultimediaRespuesta]:
        """
        Carga múltiples archivos multimedia, validándolos, guardándolos localmente y creando las entradas 
        correspondientes en la base de datos.
        Args:
            publicacion_id (int): El ID de la publicación a la que se asociarán los archivos.
            retorno_codigo (int): El código del retorno asociado a los archivos.
            archivos (list[UploadFile]): La lista de archivos a cargar.
        Returns:
            list[MultimediaRespuesta]: Una lista de respuestas con la información de los archivos cargados.
        """
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
        """
        Obtiene la lista de archivos multimedia asociados a una publicación específica.
        Args:
            publicacion_id (int): El ID de la publicación para la cual se desean obtener los archivos multimedia.
        Returns:
            list[MultimediaRespuesta]: Una lista de respuestas con la información de los archivos multimedia asociados
            a la publicación.
        """
        multimedia_list = await self.repositorio.obtener_multimedia_por_retorno(publicacion_id)
        return [MultimediaRespuesta.model_validate(m, from_attributes=True) for m in multimedia_list]
