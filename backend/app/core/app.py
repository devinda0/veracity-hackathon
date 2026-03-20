import os
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import get_settings
from app.core.exceptions import APIException
from app.core.logger import configure_logging, get_logger
from app.db.init import init_mongodb
from app.db.mongo import MongoDBClient
from app.db.qdrant import QdrantClient, init_qdrant_collections
from app.routers import api_router

settings = get_settings()
configure_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.started_at = time.time()
    app.state.mongo_db = None
    app.state.qdrant_client = None

    # Export API keys so agent submodules (langchain_google_genai etc.) can read them
    for env_var, value in {
        "GOOGLE_API_KEY": settings.GOOGLE_API_KEY,
        "GEMINI_API_KEY": settings.GEMINI_API_KEY,
        "FIRECRAWL_API_KEY": settings.FIRECRAWL_API_KEY,
        "SERPAPI_API_KEY": settings.SERPAPI_API_KEY,
    }.items():
        if value:
            os.environ.setdefault(env_var, value)

    logger.info(
        "app_startup",
        app_env=settings.APP_ENV,
        api_prefix=settings.API_PREFIX,
        version=settings.API_VERSION,
    )

    if settings.APP_ENV != "test":
        db = await MongoDBClient.connect(settings.MONGO_URI, settings.MONGO_DATABASE)
        await init_mongodb(db)
        app.state.mongo_db = db
        qdrant_client = await QdrantClient.connect()
        await init_qdrant_collections(qdrant_client)
        app.state.qdrant_client = qdrant_client

    yield

    if settings.APP_ENV != "test":
        await QdrantClient.disconnect()
        await MongoDBClient.disconnect()

    logger.info("app_shutdown", uptime_seconds=round(time.time() - app.state.started_at, 3))


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.API_VERSION,
        debug=settings.DEBUG,
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    register_middleware(app)
    register_exception_handlers(app)
    app.include_router(api_router)
    return app


def register_middleware(app: FastAPI) -> None:
    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        start = time.perf_counter()
        try:
            response = await call_next(request)
        except Exception:
            logger.exception(
                "http_request_failed",
                method=request.method,
                path=request.url.path,
            )
            raise

        duration_ms = round((time.perf_counter() - start) * 1000, 2)
        logger.info(
            "http_request",
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            duration_ms=duration_ms,
        )
        return response


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(APIException)
    async def api_exception_handler(_: Request, exc: APIException) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail, "error_code": exc.error_code},
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(_: Request, exc: RequestValidationError) -> JSONResponse:
        logger.warning("request_validation_failed", errors=exc.errors())
        return JSONResponse(
            status_code=422,
            content={"detail": "Validation failed", "errors": exc.errors()},
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(_: Request, exc: Exception) -> JSONResponse:
        logger.exception("unhandled_exception", error=str(exc))
        return JSONResponse(status_code=500, content={"detail": "Internal server error"})
