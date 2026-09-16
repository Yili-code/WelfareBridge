"""FastAPI 進入點（v2 / MongoDB / 本地 Ollama）。

    uvicorn app.main:app --reload --port 8000

啟動時：建立索引 → 同步登錄表到 MongoDB → 同步 sources.yaml → 資料庫為空時載入 seed_v2.json（真實爬取結果）→（可選）背景爬蟲。
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware



from .api import ROUTERS
from .config import Settings, get_settings
from .db import get_db, init_db
from .registry import get_registry
from .services import crawl_service, seed, tasks

log = logging.getLogger(__name__)


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or get_settings()
    logging.basicConfig(level=settings.log_level.upper(), format="%(asctime)s %(levelname)s %(name)s: %(message)s")

    @asynccontextmanager
    async def lifespan(_app: FastAPI):
        init_db()
        get_registry().sync_to_mongo(get_db())
        crawl_service.ensure_sources()
        if settings.demo_seed_on_startup:
            loaded = seed.load_seed_if_empty()
            if loaded:
                log.info("seed loaded: %d benefits", loaded)
        if settings.crawl_on_startup:
            tasks.enqueue("crawl", {"source_ids": None, "run_pipeline": True, "triggered_by": "startup"})
        yield

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description=(
            "官方補助智能搜尋與資格媒合平台 API（v2）。所有資料皆來自官方來源（gov.tw / gov.taipei / edu.tw 白名單），"
            "經語料統計關鍵字分類 → 規則式抽取 → 本地 AI 補齊 → 驗證後存入 MongoDB；每筆資料都保留原文、來源 URL 與爬取時間。"
        ),
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )
    app.add_middleware(CORSMiddleware, allow_origins=settings.cors_origin_list, allow_credentials=False, allow_methods=["GET", "POST", "OPTIONS"], allow_headers=["*"])
    app.add_middleware(GZipMiddleware, minimum_size=2048)  # 前台補助清單與比對結果是大型 JSON
    for router in ROUTERS:
        app.include_router(router)

    @app.get("/", include_in_schema=False)
    def root():
        return {"name": settings.app_name, "version": settings.app_version, "docs": "/docs", "api": "/api"}

    return app


app = create_app()
