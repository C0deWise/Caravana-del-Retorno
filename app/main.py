from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.core.config import get_settings
from app.core.database import check_db_connection, create_tables
from app.retornos.api.v1.endpoints.retorno_router import router as retornos_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s — %(name)s — %(levelname)s — %(message)s",
)
logger = logging.getLogger(__name__)
settings = get_settings()


# ─────────────────────────────────────────
#  Lifespan
# ─────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting %s v%s...", settings.APP_NAME, settings.APP_VERSION)
    check_db_connection()
    create_tables()
    logger.info("Application ready.")

    yield

    # Shutdown
    logger.info("Shutting down %s...", settings.APP_NAME)


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


# ─────────────────────────────────────────
#  Middleware
# ─────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─────────────────────────────────────────
#  Routers
# ─────────────────────────────────────────
# esta seccion esta destinada a los routers de la aplicacion
app.include_router(retornos_router)


# ─────────────────────────────────────────
#  Core endpoints
# ─────────────────────────────────────────
@app.get("/health", tags=["Health"])
def health_check():
    db_ok = check_db_connection()
    return {
        "status": "ok" if db_ok else "degraded",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "database": "connected" if db_ok else "unreachable",
    }


@app.get("/", tags=["Root"])
def root():
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs" if settings.DEBUG else "disabled",
    }