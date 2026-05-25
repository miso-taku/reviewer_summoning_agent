"use client";

import { useState, useCallback } from "react";
import {
  validateReviewForm,
  hasErrors,
  type ValidationErrors,
  type ReviewFormData,
  THEME_MAX_CHARS,
  MANUSCRIPT_BLOCK_MAX_CHARS,
} from "@/lib/validation";

interface ReviewFormProps {
  disabled: boolean;
  onSubmit: (data: ReviewFormData) => void;
}

export function ReviewForm({ disabled, onSubmit }: ReviewFormProps) {
  const [theme, setTheme] = useState("");
  const [draftBody, setDraftBody] = useState("");
  const [structureMemo, setStructureMemo] = useState("");
  const [slidesSummary, setSlidesSummary] = useState("");
  const [errors, setErrors] = useState<ValidationErrors>({});

  const handleSubmit = useCallback(
    (e: React.FormEvent) => {
      e.preventDefault();
      const data: ReviewFormData = { theme, draftBody, structureMemo, slidesSummary };
      const validationErrors = validateReviewForm(data);
      setErrors(validationErrors);
      if (!hasErrors(validationErrors)) {
        onSubmit(data);
      }
    },
    [theme, draftBody, structureMemo, slidesSummary, onSubmit]
  );

  return (
    <form onSubmit={handleSubmit} className="space-y-5" noValidate>
      <div>
        <label htmlFor="theme" className="block text-sm font-medium text-gray-700 mb-1">
          テーマ <span className="text-red-500">*</span>
        </label>
        <input
          id="theme"
          type="text"
          value={theme}
          onChange={(e) => setTheme(e.target.value)}
          disabled={disabled}
          maxLength={THEME_MAX_CHARS}
          placeholder="例: Rustのライフタイムについての技術ブログ"
          className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm shadow-sm focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 disabled:opacity-50 disabled:bg-gray-100"
          aria-describedby={errors.theme ? "theme-error" : undefined}
          aria-invalid={!!errors.theme}
        />
        {errors.theme && (
          <p id="theme-error" className="mt-1 text-sm text-red-600" role="alert">
            {errors.theme}
          </p>
        )}
      </div>

      <div>
        <label htmlFor="draft-body" className="block text-sm font-medium text-gray-700 mb-1">
          原稿本文
        </label>
        <textarea
          id="draft-body"
          value={draftBody}
          onChange={(e) => setDraftBody(e.target.value)}
          disabled={disabled}
          maxLength={MANUSCRIPT_BLOCK_MAX_CHARS}
          rows={8}
          placeholder="レビュー対象のテキストを貼り付けてください"
          className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm shadow-sm focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 disabled:opacity-50 disabled:bg-gray-100 resize-y"
          aria-describedby={errors.draftBody ? "draft-error" : undefined}
          aria-invalid={!!errors.draftBody}
        />
        {errors.draftBody && (
          <p id="draft-error" className="mt-1 text-sm text-red-600" role="alert">
            {errors.draftBody}
          </p>
        )}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label htmlFor="structure-memo" className="block text-sm font-medium text-gray-700 mb-1">
            構成メモ（任意）
          </label>
          <textarea
            id="structure-memo"
            value={structureMemo}
            onChange={(e) => setStructureMemo(e.target.value)}
            disabled={disabled}
            maxLength={MANUSCRIPT_BLOCK_MAX_CHARS}
            rows={4}
            placeholder="記事の構成案やアウトラインなど"
            className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm shadow-sm focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 disabled:opacity-50 disabled:bg-gray-100 resize-y"
            aria-describedby={errors.structureMemo ? "memo-error" : undefined}
            aria-invalid={!!errors.structureMemo}
          />
          {errors.structureMemo && (
            <p id="memo-error" className="mt-1 text-sm text-red-600" role="alert">
              {errors.structureMemo}
            </p>
          )}
        </div>

        <div>
          <label htmlFor="slides-summary" className="block text-sm font-medium text-gray-700 mb-1">
            スライド要約（任意）
          </label>
          <textarea
            id="slides-summary"
            value={slidesSummary}
            onChange={(e) => setSlidesSummary(e.target.value)}
            disabled={disabled}
            maxLength={MANUSCRIPT_BLOCK_MAX_CHARS}
            rows={4}
            placeholder="LT スライドの内容要約など"
            className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm shadow-sm focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 disabled:opacity-50 disabled:bg-gray-100 resize-y"
            aria-describedby={errors.slidesSummary ? "slides-error" : undefined}
            aria-invalid={!!errors.slidesSummary}
          />
          {errors.slidesSummary && (
            <p id="slides-error" className="mt-1 text-sm text-red-600" role="alert">
              {errors.slidesSummary}
            </p>
          )}
        </div>
      </div>

      {errors.combination && (
        <p className="text-sm text-red-600" role="alert">
          {errors.combination}
        </p>
      )}

      <button
        type="submit"
        disabled={disabled}
        aria-label="レビュー実行"
        className="inline-flex items-center rounded-md bg-indigo-600 px-5 py-2.5 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
      >
        レビュー実行
      </button>
    </form>
  );
}
