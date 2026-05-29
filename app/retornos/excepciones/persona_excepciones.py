from fastapi import HTTPException, status

class PersonaNoEncontrada(HTTPException):
    def __init__(self, pe_codigo: int):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"La persona con código {pe_codigo} no fue encontrada."
        )