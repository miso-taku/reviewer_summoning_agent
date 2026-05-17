"""依存注入: FastAPI Depends でユースケースとインフラ実装を組み立てる (TEC §8.1)。"""

from __future__ import annotations

import os
from collections.abc import Callable
from typing import Annotated

from fastapi import Depends

from review_summoning.application.use_cases.run_review_pipeline import RunReviewPipelineUseCase
from review_summoning.infrastructure.factory import build_review_pipeline_use_case

# テストで `app.dependency_overrides` と併用する型エイリアス
UseCaseFactory = Callable[[], RunReviewPipelineUseCase]

_use_case_factory: UseCaseFactory | None = None


def set_use_case_factory(factory: UseCaseFactory | None) -> None:
    """アプリ起動前またはテストでユースケース組み立てを差し替える。"""
    global _use_case_factory
    _use_case_factory = factory


def _build_use_case_from_env() -> RunReviewPipelineUseCase:
    """環境変数から PydanticAI インフラを組み立てる (TEC §8.1)。"""
    return build_review_pipeline_use_case()


def get_review_pipeline_use_case() -> RunReviewPipelineUseCase:
    if _use_case_factory is not None:
        return _use_case_factory()
    return _build_use_case_from_env()


ReviewPipelineUseCaseDep = Annotated[
    RunReviewPipelineUseCase,
    Depends(get_review_pipeline_use_case),
]


def parse_cors_origins() -> list[str]:
    raw = os.getenv("CORS_ALLOW_ORIGINS", "http://localhost:3000")
    return [origin.strip() for origin in raw.split(",") if origin.strip()]
