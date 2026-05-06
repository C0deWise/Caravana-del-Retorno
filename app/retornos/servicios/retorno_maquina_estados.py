from enum import Enum
from app.retornos.excepciones.retorno_excepciones import (
    RetornoTransicionNoPermitidaError,
    RetornoYaEnEstadoSolicitadoError
)

class RetornoEstadoTransicion:

    TRANSICIONES_VALIDAS = {
        'activo': ['en_curso'],
        'en_curso': ['finalizado'],
        'finalizado': []
    }

    RAZONES_POR_ESTADO = {
        'finalizado': "Un retorno FINALIZADO no puede cambiar de estado.",
    }
    
    @staticmethod
    def validar_transicion(estado_actual: str, nuevo_estado: str) -> None:
        """Lanza una excepción si la transición de estado no es válida."""

        if estado_actual == nuevo_estado:
            raise RetornoYaEnEstadoSolicitadoError(estado_actual)

        transiciones = RetornoEstadoTransicion.TRANSICIONES_VALIDAS.get(estado_actual, [])
        print(f"Validando transición de '{estado_actual}' a '{nuevo_estado}'. Transiciones permitidas: {transiciones}")

        if nuevo_estado not in transiciones:
            razon = RetornoEstadoTransicion.RAZONES_POR_ESTADO.get(estado_actual)
            raise RetornoTransicionNoPermitidaError(estado_actual.value, nuevo_estado.value, razon)