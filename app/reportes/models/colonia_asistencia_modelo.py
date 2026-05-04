


from pydantic import BaseModel


class ColoniaAsistencia(BaseModel):
    colonia: str
    cantidad_asistentes: int