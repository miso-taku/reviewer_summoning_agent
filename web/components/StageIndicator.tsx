"use client";

import { useEffect, useState } from "react";

interface StageIndicatorProps {
  startedAt: number;
  completed: boolean;
}

const STAGES = [
  { label: "召喚", thresholdMs: 0 },
  { label: "3名レビュー", thresholdMs: 8_000 },
  { label: "編集長統合", thresholdMs: 25_000 },
] as const;

export function StageIndicator({ startedAt, completed }: StageIndicatorProps) {
  const [elapsed, setElapsed] = useState(0);

  useEffect(() => {
    if (completed) return;
    const id = setInterval(() => {
      setElapsed(Date.now() - startedAt);
    }, 500);
    return () => clearInterval(id);
  }, [startedAt, completed]);

  return (
    <div
      className="flex items-center gap-2 text-sm"
      role="status"
      aria-label={completed ? "処理完了" : "処理中"}
      aria-live="polite"
    >
      {STAGES.map((stage, i) => {
        const isActive = !completed && elapsed >= stage.thresholdMs;
        const isDone =
          completed || (!completed && i < STAGES.length - 1 && elapsed >= STAGES[i + 1].thresholdMs);

        return (
          <div key={stage.label} className="flex items-center gap-2">
            {i > 0 && (
              <svg className="h-4 w-4 text-gray-300" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
              </svg>
            )}
            <span
              className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium transition-colors ${
                isDone || completed
                  ? "bg-green-100 text-green-800"
                  : isActive
                    ? "bg-indigo-100 text-indigo-800 font-bold"
                    : "bg-gray-100 text-gray-500"
              }`}
            >
              {isDone || completed ? (
                <svg className="h-3 w-3" fill="currentColor" viewBox="0 0 20 20" aria-hidden="true">
                  <path
                    fillRule="evenodd"
                    d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                    clipRule="evenodd"
                  />
                </svg>
              ) : isActive ? (
                <svg className="h-3 w-3 animate-spin" fill="none" viewBox="0 0 24 24" aria-hidden="true">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                </svg>
              ) : null}
              {stage.label}
            </span>
          </div>
        );
      })}
      {!completed && (
        <span className="ml-2 text-xs text-gray-400">
          {Math.floor(elapsed / 1000)}秒
        </span>
      )}
    </div>
  );
}
