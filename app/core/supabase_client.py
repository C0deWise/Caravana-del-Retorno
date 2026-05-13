"""
Cliente de Supabase para Storage.
"""
from supabase import create_client, Client
from app.core.config import get_settings

_supabase_client = None

def get_supabase_client() -> Client | None:
    """
    Retorna cliente de Supabase si está configurado.
    Si no hay credenciales, retorna None (modo local).
    """
    global _supabase_client
    
    if _supabase_client is not None:
        return _supabase_client
    
    settings = get_settings()
    
    if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
        return None  # No configurado, usar almacenamiento local
    
    _supabase_client = create_client(
        settings.SUPABASE_URL,
        settings.SUPABASE_KEY
    )
    
    return _supabase_client