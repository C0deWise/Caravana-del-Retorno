

from pydantic import BaseModel


class RegistroRetornoUsuarioDetallado(BaseModel):
    celular: str
    nombre: str
    notas: str | None
    num_hospedaje: int
    num_transporte: int
    num_parqueadero_motos: int
    num_parqueadero_carros: int
