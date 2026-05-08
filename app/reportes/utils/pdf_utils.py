"""
pdf_utils.py
------------
Utilidad para renderizar plantillas Jinja2 y convertirlas a PDF con WeasyPrint.

Instalación requerida:
    pip install weasyprint==62.3 pydyf==0.11.0

En Debian/Ubuntu también se necesitan las dependencias del sistema:
    apt-get install libpango-1.0-0 libpangoft2-1.0-0 libpangocairo-1.0-0 \
                    libgdk-pixbuf-xlib-2.0-0 libcairo2 libffi-dev
"""

from pathlib import Path

from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration
from fastapi.templating import Jinja2Templates
from fastapi.responses import Response

# Raíz del proyecto — ajusta si pdf_utils.py está en una subcarpeta distinta.
# Se usa para que WeasyPrint resuelva rutas relativas como "resources/escudo_florencia.png".
PROJECT_ROOT = Path(__file__).resolve().parents[1]  # sube desde app/reportes/utils/


def render_to_pdf(
    templates: Jinja2Templates,
    template_name: str,
    context: dict,
    filename: str = "reporte.pdf",
) -> Response:
    """
    Renderiza una plantilla Jinja2 y la convierte a PDF con WeasyPrint.

    Args:
        templates:     Instancia de Jinja2Templates del proyecto.
        template_name: Nombre del archivo de plantilla (ej: "reporte_colonia.html").
        context:       Diccionario de variables para la plantilla.
                       Debe incluir la clave "request".
        filename:      Nombre sugerido del archivo PDF en la respuesta HTTP.

    Returns:
        Response de FastAPI con el PDF en el body y los headers correctos.
    """
    # 1. Renderizar el HTML con Jinja2
    template = templates.get_template(template_name)
    html_str = template.render(context)

    # 2. Convertir a PDF con WeasyPrint
    #    base_url permite que WeasyPrint resuelva rutas relativas (imágenes, fuentes)
    #    partiendo desde la raíz del proyecto.
    font_config = FontConfiguration()
    pdf_bytes = HTML(
        string=html_str,
        base_url=str(PROJECT_ROOT),   # ← clave para resolver "resources/escudo_florencia.png"
    ).write_pdf(
        font_config=font_config,
        stylesheets=[
            CSS(
                string="""
                    @page {
                        size: A4;
                        margin: 1cm 1.5cm;
                    }
                    body {
                        -webkit-print-color-adjust: exact;
                        print-color-adjust: exact;
                    }
                    .no-print { display: none !important; }
                """,
                font_config=font_config,
            )
        ],
    )

    # 3. Devolver como respuesta HTTP con tipo MIME correcto
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'inline; filename="{filename}"',
            "Content-Length": str(len(pdf_bytes)),
        },
    )