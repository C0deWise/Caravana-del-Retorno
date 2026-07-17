"""
    main.py punto de entrada de la app FASTAPI, contiene el middleware,
    el registro de routers y los endpoints básicos como /health, /docs y /.
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging

from app.excepciones import AppException

from app.core.config import get_settings
from app.core.database import check_db_connection, create_tables
from app.usuarios.models.usuario import Rol
from app.usuarios.models.parentesco import Parentesco
from app.colonias.models.colonia_model import Colonia
from app.colonias.models.solicitud_colonia import SolicitudColonia
from app.multimedia.modelos.multimedia_modelo import Multimedia
from app.retornos.modelos.retorno_modelo import Retorno
from app.retornos.modelos.registro_retorno_modelo import RegistroRetorno
from app.retornos.modelos.grupo_retorno_modelo import GrupoRetorno
from app.retornos.modelos.persona_modelo import Persona
from app.retornos.modelos.registro_retorno_grupo_modelo import RegistroRetornoGrupo
from app.retornos.modelos.retorno_grupo_usuario_modelo import RetornoGrupoUsuario
from app.retornos.modelos.solicitud_grupo_retorno_modelo import SolicitudGrupoRetorno
from app.publicacion.modelos.publicacion_modelo import Publicacion
from app.retornos.modelos.persona_grupo_retorno_modelo import persona_grupo_retorno
from scripts.seed_eventos import seed_eventos
from scripts.seed_roles import seed_roles
from scripts.seed_data import seed_data
import app.core.scheduler as scheduler

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s — %(name)s — %(levelname)s — %(message)s",
)
logger = logging.getLogger(__name__)
settings = get_settings()



#  Lifespan

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting %s v%s...", settings.APP_NAME, settings.APP_VERSION)
    await check_db_connection()
    
    # IMPORTANTE: No usar create_tables() junto con Alembic. 
    # Alembic gestiona la creación mediante 'alembic upgrade head' en el entrypoint.sh.
    
    print(">>> lifespan ejecutándose")
    #await create_tables()  # Solo para desarrollo, en producción usar Alembic
    # Ejecutar seed de roles automáticamente al iniciar la app
    logger.info("Verificando e insertando roles iniciales...")
    await seed_roles()
    
    logger.info("Creacion de eventos")
    await seed_eventos()
    # Ejecutar seed de datos de prueba
    logger.info("Cargando datos de prueba...")
    await seed_data()

    logger.info("Application ready.")

    yield

    # Shutdown
    logger.info("Shutting down %s...", settings.APP_NAME)
    scheduler.shutdown()


# ─────────────────────────────────────────
#  App instance
# ─────────────────────────────────────────
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=settings.APP_DESCRIPTION,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    lifespan=lifespan,
)


@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )



#  Middleware
# ─────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS,
    allow_origin_regex=r"https://caravana-del-retorno-frontend(-[a-z0-9-]+)?\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─────────────────────────────────────────
#  Routers
# ─────────────────────────────────────────
# esta seccion esta destinada a los routers de la aplicacion
from app.colonias.api.v1.router import router as colonia_router
from app.retornos.api.v1.router import api_router as retornos_module_router
from app.usuarios.api.v1.usuario_router import router as usuario_router
from app.multimedia.api.v1.endpoints.multimedia_router import router as multimedia_router
from app.publicacion.api.v1.endpoints.publicacion_router import router as publicacion_router
from app.reportes.api.v1.router import router as reportes_router
from app.notificaciones.api.v1.router import router as notificaciones_router
from app.correos.api.v1.router import router as correos_router
prefix = "/api/v1"
app.include_router(colonia_router, prefix=prefix)
app.include_router(usuario_router, prefix=prefix)
app.include_router(retornos_module_router, prefix=prefix)
app.include_router(multimedia_router, prefix=prefix)
app.include_router(publicacion_router, prefix=prefix)
app.include_router(reportes_router, prefix=prefix)
app.include_router(notificaciones_router, prefix=prefix)
app.include_router(correos_router, prefix=prefix)



# ─────────────────────────────────────────
#  Core endpoints
# ─────────────────────────────────────────
@app.get("/health", tags=["Health"])
async def health_check():
    db_ok = await check_db_connection()
    return {
        "status": "ok" if db_ok else "degraded",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "database": "connected" if db_ok else "unreachable",
    }


@app.get("/", tags=["Root"])
async def root():
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs" if settings.DEBUG else "disabled",
    }