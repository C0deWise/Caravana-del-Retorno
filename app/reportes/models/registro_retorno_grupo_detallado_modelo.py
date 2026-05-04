



from pydantic import BaseModel


class RegistroRetornoGrupoDetallado(BaseModel):
    cod_grupo: int
    lider_nombre: str
    lider_celular: str
    nombre_usuarios: list[str]
    notas: str | None
    num_hospedaje: int 
    num_transporte: int
    num_parqueadero_motos: int
    num_parqueadero_carros: int