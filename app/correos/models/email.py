"""
Modelo de dominio del módulo de correos.
"""
from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class EmailMessage:
    """Representa un correo listo para ser enviado por el repository."""

    recipients: List[str]
    subject: str
    template_name: str
    context: Dict[str, str] = field(default_factory=dict)
    subtype: str = "html"
