"""Contrato RBAC contra la matriz del documento de proteccion por roles.

Este test inspecciona rutas FastAPI y sus dependencias para verificar que
cada endpoint documentado tenga los roles esperados con require_roles(...).
"""

from __future__ import annotations

import sys
import types
from typing import Any, Optional

from fastapi.routing import APIRoute

# Evita cargar librerias nativas de WeasyPrint durante la recoleccion de tests.
# Para este contrato RBAC solo necesitamos el enrutado, no renderizado PDF.
if "weasyprint" not in sys.modules:
    fake_weasyprint = types.ModuleType("weasyprint")
    fake_weasyprint.__path__ = []
    fake_weasyprint_text = types.ModuleType("weasyprint.text")
    fake_weasyprint_fonts = types.ModuleType("weasyprint.text.fonts")

    class _DummyHTML:
        def __init__(self, *args, **kwargs):
            # Stub intencional para pruebas de enrutado sin motor PDF.
            return None

        def write_pdf(self, *args, **kwargs):
            return b""

    class _DummyCSS:
        def __init__(self, *args, **kwargs):
            # Stub intencional para pruebas de enrutado sin motor PDF.
            return None

    class _DummyFontConfiguration:
        def __init__(self, *args, **kwargs):
            # Stub intencional para pruebas de enrutado sin motor PDF.
            return None

    fake_weasyprint_any = fake_weasyprint  # type: Any
    fake_weasyprint_fonts_any = fake_weasyprint_fonts  # type: Any
    fake_weasyprint_any.HTML = _DummyHTML
    fake_weasyprint_any.CSS = _DummyCSS
    fake_weasyprint_fonts_any.FontConfiguration = _DummyFontConfiguration

    sys.modules["weasyprint"] = fake_weasyprint
    sys.modules["weasyprint.text"] = fake_weasyprint_text
    sys.modules["weasyprint.text.fonts"] = fake_weasyprint_fonts

from app.main import app

# Roles oficiales por codigo:
# 1=retornante, 2=lider, 3=administrativo, 4=visitante
RBAC_EXPECTATIONS: dict[tuple[str, str], set[int]] = {
    # Colonias
    ("GET", "/api/v1/colonias/"): {3},
    ("POST", "/api/v1/colonias/"): {3},
    ("PATCH", "/api/v1/colonias/solicitud-colonia/{codigo}/aceptar"): {2},
    ("PATCH", "/api/v1/colonias/solicitud-colonia/{codigo}/rechazar"): {2},
    ("GET", "/api/v1/colonias/{colonia_codigo}"): {1, 2, 3},
    ("POST", "/api/v1/colonias/crear-solicitud"): {1},
    ("GET", "/api/v1/colonias/solicitudes-pendientes/{cod_colonia}"): {2, 3},
    ("GET", "/api/v1/colonias/solicitudes-recientes/{cod_colonia}"): {2, 3},
    ("GET", "/api/v1/colonias/solicitudes-recientes-usuario/{cod_usuario}"): {1, 2, 3},
    ("PATCH", "/api/v1/colonias/establecer_lider/{colonia_codigo}/"): {3},
    ("PATCH", "/api/v1/colonias/desactivar/{colonia_codigo}/"): {3},
    ("GET", "/api/v1/colonias/colonias-activas/"): {1, 2, 3},
    ("PATCH", "/api/v1/colonias/cambiar-lider/{colonia_codigo}/"): {3},
    ("PATCH", "/api/v1/colonias/sacar-miembro/{colonia_codigo}/"): {2, 3},
    # Usuario
    ("POST", "/api/v1/usuario/registrar"): set(),
    ("POST", "/api/v1/usuario/solicitar-parentesco"): {1, 2},
    ("GET", "/api/v1/usuario/"): {3},
    ("GET", "/api/v1/usuario/buscar_id/{usuario_id}"): {2, 3},
    ("GET", "/api/v1/usuario/nombres"): {1, 2, 3},
    ("GET", "/api/v1/usuario/todos"): {3},
    ("GET", "/api/v1/usuario/buscar/{nombre}"): {1, 2, 3},
    ("GET", "/api/v1/usuario/buscar_documento/{documento}"): {2, 3},
    ("GET", "/api/v1/usuario/{codigo_usuario}/parentescos"): {1, 2},
    ("GET", "/api/v1/usuario/colonia/{colonia}"): {1, 2, 3},
    # Retornos
    ("GET", "/api/v1/retornos/"): set(),
    ("POST", "/api/v1/retornos/"): {3},
    ("PUT", "/api/v1/retornos/editar-registro/{registro_id}"): {1, 2},
    ("GET", "/api/v1/retornos/esta-registrado-retorno/{us_codigo}/{re_codigo}"): {1, 2, 3},
    ("GET", "/api/v1/retornos/vigente"): set(),
    ("GET", "/api/v1/retornos/{codigo}"): set(),
    ("PATCH", "/api/v1/retornos/{codigo}/estado"): {3},
    ("POST", "/api/v1/retornos/registro"): {1, 2},
    ("GET", "/api/v1/retornos/registro/usuario/{usuario_id}/retorno/{retorno_id}"): {1, 2, 3},
    ("DELETE", "/api/v1/retornos/darse-de-baja"): {1, 2},
    # GrupoRetorno
    ("POST", "/api/v1/grupoRetorno/"): {1, 2},
    ("GET", "/api/v1/grupoRetorno/lider/{us_codigo_lider}"): {1, 2, 3},
    ("GET", "/api/v1/grupoRetorno/{gr_codigo}/lider"): {1, 2, 3},
    ("POST", "/api/v1/grupoRetorno/solicitar-miembro"): {1, 2},
    ("POST", "/api/v1/grupoRetorno/registro"): {1, 2},
    ("GET", "/api/v1/grupoRetorno/{gr_codigo}/miembros"): {1, 2, 3},
    ("PATCH", "/api/v1/grupoRetorno/solicitudes/aceptar/{solicitud_id}"): {1, 2},
    ("PATCH", "/api/v1/grupoRetorno/solicitudes/rechazar/{solicitud_id}"): {1, 2},
    ("GET", "/api/v1/grupoRetorno/solicitudes/recientes/usuario/{usuario_id}"): {1, 2, 3},
    ("GET", "/api/v1/grupoRetorno/solicitudes/grupo/{grupo_retorno_id}"): {1, 2, 3},
    ("GET", "/api/v1/grupoRetorno/grupo/usuario/{usuario_id}/{retorno_id}"): {1, 2, 3},
    ("GET", "/api/v1/grupoRetorno/grupo/usuarios/{gr_codigo}/"): {1, 2, 3},
    ("GET", "/api/v1/grupoRetorno/registro/{gr_codigo}/{re_codigo}"): {1, 2, 3},
    ("PATCH", "/api/v1/grupoRetorno/registro/{registro_id}"): {1, 2, 3},
    # Personas
    ("GET", "/api/v1/personas/"): {1, 2, 3},
    ("POST", "/api/v1/personas/"): {1, 2, 3},
    ("POST", "/api/v1/personas/asociar-grupo"): {1, 2, 3},
    ("GET", "/api/v1/personas/grupo/{gr_codigo}"): {1, 2, 3},
    ("GET", "/api/v1/personas/{pe_codigo}"): {1, 2, 3},
    ("GET", "/api/v1/personas/documento/{documento}"): {1, 2, 3},
    ("GET", "/api/v1/personas/registro-documento/{pe_documento}/{re_codigo}"): {1, 2, 3},
    ("GET", "/api/v1/personas/registro-id/{pe_codigo}/{re_codigo}"): {1, 2, 3},
    # Multimedia
    ("POST", "/api/v1/cargar-multimedia/{retorno_codigo}"): {2, 3},
    # Publicaciones
    ("POST", "/api/v1/crear-publicacion/"): {2, 3},
    ("GET", "/api/v1/obtener-publicaciones-retorno/{retorno_id}/"): set(),
    # Reportes
    ("GET", "/api/v1/reportes/reporte-asistencia-colonia/{retorno_id}/{colonia_id}"): {2, 3},
    ("GET", "/api/v1/reportes/reporte-general-asistencia/{retorno_id}"): {2, 3},
}


def _extract_role_set_from_callable(callable_obj) -> Optional[set[int]]:
    """Extrae los codigos de rol capturados por require_roles(*roles)."""
    if callable_obj is None:
        return None

    if callable_obj.__module__ != "app.usuarios.auth_dependencies" or callable_obj.__name__ != "_checker":
        return None

    closure = getattr(callable_obj, "__closure__", None) or []
    for cell in closure:
        value = cell.cell_contents
        if isinstance(value, tuple) and value and all(isinstance(item, int) for item in value):
            return set(value)

    return None


def _walk_dependant_for_roles(dependant) -> Optional[set[int]]:
    role_set = _extract_role_set_from_callable(getattr(dependant, "call", None))
    if role_set is not None:
        return role_set

    for child in getattr(dependant, "dependencies", []):
        nested = _walk_dependant_for_roles(child)
        if nested is not None:
            return nested

    return None


def _collect_api_routes() -> dict[tuple[str, str], APIRoute]:
    routes: dict[tuple[str, str], APIRoute] = {}
    for route in app.routes:
        if not isinstance(route, APIRoute):
            continue
        for method in route.methods:
            key = (method.upper(), route.path)
            routes[key] = route
    return routes


def _format_key(key: tuple[str, str]) -> str:
    return f"{key[0]} {key[1]}"


def test_documented_endpoints_exist_in_app_routes() -> None:
    api_routes = _collect_api_routes()

    missing = [key for key in RBAC_EXPECTATIONS if key not in api_routes]

    assert not missing, "Endpoints del documento no encontrados en FastAPI: " + ", ".join(
        _format_key(key) for key in missing
    )


def test_documented_endpoints_match_expected_role_matrix() -> None:
    api_routes = _collect_api_routes()
    mismatches: list[str] = []

    for key, expected_roles in RBAC_EXPECTATIONS.items():
        route = api_routes[key]
        detected_roles = _walk_dependant_for_roles(route.dependant)
        normalized_detected = detected_roles or set()

        if normalized_detected != expected_roles:
            mismatches.append(
                f"{_format_key(key)} -> esperado={sorted(expected_roles)} detectado={sorted(normalized_detected)}"
            )

    assert not mismatches, "Matriz RBAC fuera de contrato:\n" + "\n".join(mismatches)
