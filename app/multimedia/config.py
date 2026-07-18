from app.multimedia.modelos.multimedia_modelo import FormatoMultimedia, TipoMultimedia

EXTENSIONES_POR_TIPO = {
    (TipoMultimedia.IMAGEN, FormatoMultimedia.JPG): [".jpg"],
    (TipoMultimedia.IMAGEN, FormatoMultimedia.JPEG): [".jpeg"],
    (TipoMultimedia.IMAGEN, FormatoMultimedia.PNG): [".png"],
    (TipoMultimedia.IMAGEN, FormatoMultimedia.GIF): [".gif"],
    (TipoMultimedia.VIDEO, FormatoMultimedia.MP4): [".mp4"],
    (TipoMultimedia.VIDEO, FormatoMultimedia.AVI): [".avi"],
    (TipoMultimedia.VIDEO, FormatoMultimedia.MOV): [".mov"],
    (TipoMultimedia.VIDEO, FormatoMultimedia.MKV): [".mkv"],
    (TipoMultimedia.DOCUMENTO, FormatoMultimedia.PDF): [".pdf"],
}