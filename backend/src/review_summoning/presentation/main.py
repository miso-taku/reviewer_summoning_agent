"""FastAPI アプリケーションエントリポイント (TEC §7 / §8.1)。"""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from review_summoning.presentation.api.v1.review import router as review_router
from review_summoning.presentation.dependencies import parse_cors_origins
from review_summoning.presentation.exception_handlers import register_exception_handlers


def create_app() -> FastAPI:
    app = FastAPI(
        title="レビュアー召喚 API",
        version="0.1.0",
        description="POST /api/v1/review — 召喚・3 名並列レビュー・編集長統合",
    )

    origins = parse_cors_origins()
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_methods=["POST", "OPTIONS"],
        allow_headers=["Content-Type", "Accept"],
    )

    register_exception_handlers(app)
    app.include_router(review_router, prefix="/api/v1")

    return app


app = create_app()
