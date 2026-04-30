from enum import Enum

class TipoMultimedia(str, Enum):
    IMAGEN = "imagen"
    VIDEO = "video"

EXTENSIONES_IMAGEN = {'.jpg', '.jpeg', '.png', '.gif'}
EXTENSIONES_VIDEO = {'.mp4', '.avi', '.mov', '.mkv'}

EXTENSIONES_POR_TIPO = {
    TipoMultimedia.IMAGEN: EXTENSIONES_IMAGEN,
    TipoMultimedia.VIDEO: EXTENSIONES_VIDEO
}