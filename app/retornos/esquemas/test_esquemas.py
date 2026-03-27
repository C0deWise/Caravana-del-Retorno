import pytest
from pydantic import ValidationError
from datetime import datetime
from app.retornos.esquemas.retorno_esquemas import RetornoCreate, RetornoResponse

def test_retorno_create_valid():
    """Prueba que RetornoCreate acepta datos válidos."""
    payload = {
        "anio": 2024,
        "estado": "activo"
    }
    retorno = RetornoCreate(**payload)
    assert retorno.anio == 2024
    assert retorno.estado == "activo"

def test_retorno_create_invalid_type():
    """Prueba que RetornoCreate falla si el año no es un entero."""
    payload = {
        "anio": "dos mil veinticuatro", # Tipo inválido
        "estado": "activo"
    }
    with pytest.raises(ValidationError) as excinfo:
        RetornoCreate(**payload)  # type: ignore
    
    # Verificamos que el error sea sobre anio
    errors = excinfo.value.errors()
    assert any(e["loc"] == ("anio",) for e in errors)

def test_retorno_response_from_attributes():
    """Prueba que RetornoResponse puede crearse desde atributos (modo ORM)."""
    data = {
        "codigo": 1,
        "fecha_creacion": datetime.now(),
        "anio": 2025,
        "estado": "finalizado"
    }
    response = RetornoResponse(**data)
    assert response.codigo == 1
    assert response.estado == "finalizado"