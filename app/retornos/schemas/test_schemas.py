import pytest
from pydantic import ValidationError
from datetime import datetime
from app.retornos.schemas.retorno_schemas import RetornoCreate, RetornoResponse

def test_retorno_create_valid():
    """Prueba que RetornoCreate acepta datos válidos."""
    payload = {
        "re_anio": 2024,
        "re_estado": "activo"
    }
    retorno = RetornoCreate(**payload)
    assert retorno.re_anio == 2024
    assert retorno.re_estado == "activo"

def test_retorno_create_invalid_type():
    """Prueba que RetornoCreate falla si el año no es un entero."""
    payload = {
        "re_anio": "dos mil veinticuatro", # Tipo inválido
        "re_estado": "activo"
    }
    with pytest.raises(ValidationError) as excinfo:
        RetornoCreate(**payload)  # type: ignore
    
    # Verificamos que el error sea sobre re_anio
    errors = excinfo.value.errors()
    assert any(e["loc"] == ("re_anio",) for e in errors)

def test_retorno_response_from_attributes():
    """Prueba que RetornoResponse puede crearse desde atributos (modo ORM)."""
    data = {
        "re_codigo": 1,
        "re_fecha_creacion": datetime.now(),
        "re_anio": 2025,
        "re_estado": "finalizado"
    }
    response = RetornoResponse(**data)
    assert response.re_codigo == 1
    assert response.re_estado == "finalizado"