from fastapi import HTTPException, status

class GrupoNoEncontrado(HTTPException):
    def __init__(self, gr_codigo: int):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"El grupo con código {gr_codigo} no fue encontrado."
        )