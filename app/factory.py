from asyncio import to_thread
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.config import get_settings
from app.core.database import DatabasePool
from app.core.errors import register_exception_handlers
from app.core.logging import configure_logging
from app.ws.manager import ConnectionManager
from app.ws.router import websocket_router


def app() -> FastAPI:
    settings = get_settings()
    configure_logging(settings.log_level)
    database = DatabasePool(
        dsn=settings.database_url,
        min_size=settings.database_pool_min_size,
        max_size=settings.database_pool_max_size,
    )
    connections = ConnectionManager()

    @asynccontextmanager
    async def lifespan(_: FastAPI):
        await to_thread(database.open)
        try:
            yield
        finally:
            await to_thread(database.close)

    application = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        debug=settings.debug,
        lifespan=lifespan,
    )
    application.state.database = database
    application.state.websocket_connections = connections
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    register_exception_handlers(application)
    application.include_router(api_router, prefix=settings.api_prefix)
    application.include_router(websocket_router, prefix=settings.api_prefix)
    return application
