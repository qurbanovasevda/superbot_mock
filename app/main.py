import logging
import sqlite3
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.config import Settings
from app.repositories.catalog import Catalog
from app.repositories.json_repository import DataSourceError

from app.visual_search import router as visual_router
from app.ui import router as ui_router
from app.llm_chat import LLMConversation, GeminiPlanner
from app.chat import ConversationEngine, router as chat_router
from app.api import router
from app.services.catalog_service import CatalogService, DomainError
from app.services.state import StateStore

logger = logging.getLogger(__name__)


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or Settings()

    @asynccontextmanager
    async def lifespan(application: FastAPI):
        application.state.catalog = None
        try:
            application.state.catalog = Catalog.load(settings.data_dir)
            application.state.service = CatalogService(application.state.catalog)
            application.state.store = StateStore(settings.database_path, application.state.service)
            if settings.chat_mode not in ("llm", "rules"):
                raise ValueError("SUPERCHAT_CHAT_MODE must be llm or rules")
            application.state.store.chat = (LLMConversation(application.state.store, settings.reference_date, GeminiPlanner(settings))
                                             if settings.chat_mode == "llm" else ConversationEngine(application.state.store, settings.reference_date))
        except DataSourceError:
            logger.error("Mock datasets could not be loaded")
        yield

    application = FastAPI(title=settings.application_name, lifespan=lifespan)

    application.include_router(router)
    application.include_router(chat_router)
    application.include_router(ui_router)
    application.include_router(visual_router)

    @application.exception_handler(DomainError)
    async def domain_error(request: Request, exc: DomainError):
        return JSONResponse(status_code=exc.status, content={"message": exc.message})

    @application.exception_handler(sqlite3.Error)
    async def storage_error(request: Request, exc: sqlite3.Error):
        logger.error("Local state storage is unavailable")
        return JSONResponse(status_code=503, content={"message": "Session storage is temporarily unavailable. Please try again."})

    @application.get("/health")
    def health(request: Request):
        catalog = request.app.state.catalog
        if catalog is None:
            return JSONResponse(status_code=503, content={
                "status": "unavailable", "message": "Mock datasets are unavailable."
            })
        return {"status": "ok", "phase": 1, "stage": 5,
                "reference_date": settings.reference_date.isoformat(),
                "chat_mode": settings.chat_mode, "llm_provider": "gemini" if settings.chat_mode == "llm" else None, "llm_configured": bool(settings.gemini_api_key),
                "datasets": catalog.counts()}

    return application


app = create_app()
