"""application.mappers: ドメイン結果 → presentation DTO の純粋マッピング。"""

from review_summoning.application.mappers.review_pipeline import (
    map_completed_session_to_success_response,
)

__all__ = ["map_completed_session_to_success_response"]
