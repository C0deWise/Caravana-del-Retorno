


from pydantic import BaseModel


class NecesidadesTotales(BaseModel):
    num_hospedaje: int
    num_transporte: int
    num_parqueadero_motos: int
    num_parqueadero_carros: int