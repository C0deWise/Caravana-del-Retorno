from app.colonias.schemas.colonia_schemas import ColoniaCrear
import pytest

def test_crear_colonia_valida():
    colonia = ColoniaCrear(
        pais = "colombia",
        departamento = "cauca",
        ciudad = "popayán"
    )

    assert colonia.pais == "Colombia"
    assert colonia.departamento == "Cauca"
    assert colonia.ciudad == "Popayán"

def test_crear_colonia_extranjera_valida():
    colonia = ColoniaCrear(
        pais = "francia"
    )

    assert colonia.pais == "Francia"

def test_crear_colonia_colombia_con_lider():
    colonia = ColoniaCrear(
        pais = "colombia",
        departamento = "antioquia",
        ciudad = "medellín",
        lider_id = 2
    )

    assert colonia.pais == "Colombia"
    assert colonia.departamento == "Antioquia"
    assert colonia.ciudad == "Medellín"
    assert colonia.lider_id == 2

def test_crear_colonia_extranjera_con_lider():
    colonia = ColoniaCrear(
        pais = "españa",
        lider_id = 3
    )

    assert colonia.pais == "España"
    assert colonia.lider_id == 3

def test_crear_colonia_colombia_sin_departamento_ciudad():
    with pytest.raises(ValueError):
        ColoniaCrear(
            pais = "colombia",
            departamento = None,
            ciudad = None
        )

def test_crear_colonia_extranjera_con_departamento_ciudad():
    with pytest.raises(ValueError):
        ColoniaCrear(
            pais = "francia",
            departamento = "cauca",
            ciudad = "popayán"
        )

def test_crear_colonia_con_caracteres_invalidos():
    with pytest.raises(ValueError):
        ColoniaCrear(
            pais = "colombia123",
            departamento = "cauca!",
            ciudad = "popayán@"
        )

def test_crear_colonia_con_campos_vacios():
    with pytest.raises(ValueError):
        ColoniaCrear(
            pais = None,
            departamento = None,
            ciudad = None
        )