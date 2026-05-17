"""インフラ実装の組み立て (presentation DI から利用)。"""

from __future__ import annotations

from review_summoning.application.use_cases.run_review_pipeline import RunReviewPipelineUseCase
from review_summoning.infrastructure.config import Settings
from review_summoning.infrastructure.llm.pydantic_ai_editor import PydanticAiEditorIntegration
from review_summoning.infrastructure.llm.pydantic_ai_review import PydanticAiSingleReview
from review_summoning.infrastructure.llm.pydantic_ai_summoning import PydanticAiReviewerSummoning


def build_review_pipeline_use_case(settings: Settings | None = None) -> RunReviewPipelineUseCase:
    cfg = settings or Settings()
    cfg.configure_logging()
    return RunReviewPipelineUseCase(
        summoning=PydanticAiReviewerSummoning(cfg),
        single_review=PydanticAiSingleReview(cfg),
        editor=PydanticAiEditorIntegration(cfg),
    )
