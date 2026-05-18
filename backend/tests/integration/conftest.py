"""IT-API 結合テスト用フィクスチャ (test-plan §3.2)。"""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from httpx import ASGITransport, AsyncClient

from review_summoning.application.use_cases.run_review_pipeline import RunReviewPipelineUseCase
from review_summoning.presentation.dependencies import get_review_pipeline_use_case
from review_summoning.presentation.main import create_app


class UseCaseWithPipelineTimeout:
    """ルータ経由でも短いパイプラインタイムアウトを検証するための薄いラッパ。"""

    def __init__(self, inner: RunReviewPipelineUseCase, *, pipeline_timeout_seconds: float) -> None:
        self._inner = inner
        self._pipeline_timeout_seconds = pipeline_timeout_seconds

    async def execute(self, command, **kwargs):
        return await self._inner.execute(
            command,
            pipeline_timeout_seconds=self._pipeline_timeout_seconds,
            **kwargs,
        )


@asynccontextmanager
async def api_client_for(use_case: RunReviewPipelineUseCase) -> AsyncIterator[AsyncClient]:
    """スタブユースケースを DI した httpx AsyncClient (IT-API 用)。"""
    app = create_app()
    app.dependency_overrides[get_review_pipeline_use_case] = lambda: use_case
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client
    app.dependency_overrides.clear()
