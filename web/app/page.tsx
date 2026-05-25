"use client";

import { useCallback, useState } from "react";
import { Header } from "@/components/Header";
import { ReviewForm } from "@/components/ReviewForm";
import { StageIndicator } from "@/components/StageIndicator";
import { ResultSection } from "@/components/ResultSection";
import { ErrorDisplay } from "@/components/ErrorDisplay";
import {
  postReview,
  ApiError,
  NetworkError,
  TimeoutError,
} from "@/lib/api-client";
import type { ReviewFormData } from "@/lib/validation";
import type { AppState } from "@/lib/types";

function errorToMessage(err: unknown): string {
  if (err instanceof ApiError) {
    const { status, errorBody } = err;
    switch (errorBody.code) {
      case "VALIDATION_ERROR":
        return errorBody.message;
      case "LLM_UPSTREAM_ERROR":
        return "AI 側でエラーが発生しました。時間をおいて再試行してください。";
      case "LLM_UNAVAILABLE":
        return "AI サービスが一時的に利用できません。";
      case "REQUEST_TIMEOUT":
        return "処理がタイムアウトしました。原文を短くするか再試行してください。";
      default:
        return `サーバーエラー (HTTP ${status}): ${errorBody.message}`;
    }
  }
  if (err instanceof TimeoutError) return err.message;
  if (err instanceof NetworkError) return err.message;
  return "予期しないエラーが発生しました。";
}

export default function HomePage() {
  const [state, setState] = useState<AppState>({ kind: "idle" });

  const handleSubmit = useCallback(async (data: ReviewFormData) => {
    setState({ kind: "loading", startedAt: Date.now() });

    try {
      const result = await postReview({
        theme: data.theme.trim(),
        draft_body: data.draftBody.trim() || null,
        structure_memo: data.structureMemo.trim() || null,
        slides_summary: data.slidesSummary.trim() || null,
      });
      setState({ kind: "result", data: result });
    } catch (err) {
      setState({ kind: "error", message: errorToMessage(err) });
    }
  }, []);

  return (
    <>
      <Header />
      <main className="flex-1 mx-auto w-full max-w-5xl px-4 py-8 space-y-8">
        <section aria-label="レビュー依頼フォーム">
          <ReviewForm
            disabled={state.kind === "loading"}
            onSubmit={handleSubmit}
          />
        </section>

        {state.kind === "loading" && (
          <section aria-label="処理中">
            <StageIndicator startedAt={state.startedAt} completed={false} />
          </section>
        )}

        {state.kind === "result" && (
          <section aria-label="レビュー結果">
            <StageIndicator startedAt={0} completed={true} />
            <div className="mt-6">
              <ResultSection data={state.data} />
            </div>
          </section>
        )}

        {state.kind === "error" && (
          <section aria-label="エラー">
            <ErrorDisplay message={state.message} />
          </section>
        )}
      </main>
    </>
  );
}
