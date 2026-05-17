"""LLM 出力・制約の定数 (TEC §5.2)。"""

MAX_REVIEW_ARRAY_ITEMS = 50
MAX_PRIORITY_FIXES = 20

# 個別 LLM 呼び出しの既定上限 (秒)。全体 170s バジェット内に収める目安
DEFAULT_LLM_CALL_TIMEOUT_SECONDS = 55.0
