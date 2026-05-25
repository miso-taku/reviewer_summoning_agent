/**
 * API クライアント (TEC §14)。
 * POST /api/v1/review に対する fetch ラッパー。180s タイムアウト付き。
 */

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://127.0.0.1:8000";

const CLIENT_TIMEOUT_MS = 180_000;

export interface ReviewRequest {
  theme: string;
  draft_body: string | null;
  structure_memo: string | null;
  slides_summary: string | null;
}

export interface ReviewerOut {
  id: string;
  display_name: string;
  specialty_axis: string;
  perspective: string;
}

export interface ReviewItemOut {
  reviewer_id: string;
  good_points: string[];
  issues: string[];
  concrete_fixes: string[];
}

export interface PriorityFixOut {
  rank: number;
  summary: string;
  related_reviewer_ids: string[];
}

export interface EditorOut {
  integrated_comment: string;
  priority_fixes: PriorityFixOut[];
  deduplication_notes: string;
}

export interface MetaOut {
  request_id: string;
  completed_at: string;
}

export interface ReviewSuccessResponse {
  reviewers: ReviewerOut[];
  reviews: ReviewItemOut[];
  editor: EditorOut;
  meta: MetaOut;
}

export interface ErrorDetail {
  field: string;
  issue: string;
}

export interface ErrorBody {
  code: string;
  message: string;
  details?: ErrorDetail[];
}

export interface ErrorEnvelope {
  error: ErrorBody;
}

export class ApiError extends Error {
  constructor(
    public readonly status: number,
    public readonly errorBody: ErrorBody
  ) {
    super(errorBody.message);
    this.name = "ApiError";
  }
}

export class NetworkError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "NetworkError";
  }
}

export class TimeoutError extends Error {
  constructor() {
    super("処理がタイムアウトしました。原文を短くするか再試行してください。");
    this.name = "TimeoutError";
  }
}

export async function postReview(
  request: ReviewRequest,
  signal?: AbortSignal
): Promise<ReviewSuccessResponse> {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), CLIENT_TIMEOUT_MS);

  const combinedSignal = signal
    ? mergeAbortSignals(signal, controller.signal)
    : controller.signal;

  try {
    const res = await fetch(`${API_BASE_URL}/api/v1/review`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(request),
      signal: combinedSignal,
    });

    if (!res.ok) {
      let errorBody: ErrorBody;
      try {
        const envelope: ErrorEnvelope = await res.json();
        errorBody = envelope.error;
      } catch {
        errorBody = {
          code: "UNKNOWN",
          message: `サーバーエラー (HTTP ${res.status})`,
        };
      }
      throw new ApiError(res.status, errorBody);
    }

    return (await res.json()) as ReviewSuccessResponse;
  } catch (err) {
    if (err instanceof ApiError) throw err;
    if (err instanceof DOMException && err.name === "AbortError") {
      if (signal?.aborted) throw new NetworkError("リクエストが中断されました。");
      throw new TimeoutError();
    }
    if (err instanceof TypeError) {
      throw new NetworkError(
        "ネットワークに接続できませんでした。API サーバーが起動しているか確認してください。"
      );
    }
    throw err;
  } finally {
    clearTimeout(timeoutId);
  }
}

function mergeAbortSignals(...signals: AbortSignal[]): AbortSignal {
  const controller = new AbortController();
  for (const signal of signals) {
    if (signal.aborted) {
      controller.abort(signal.reason);
      return controller.signal;
    }
    signal.addEventListener("abort", () => controller.abort(signal.reason), {
      once: true,
    });
  }
  return controller.signal;
}
