/**
 * FUN §5.1 に基づくクライアント検証定数・関数。
 * バックエンド (domain/value_objects) と同一の制約を再現する。
 */

export const THEME_MAX_CHARS = 2000;
export const MANUSCRIPT_BLOCK_MAX_CHARS = 100_000;
export const TOTAL_INPUT_MAX_CHARS = 200_000;

export interface ValidationErrors {
  theme?: string;
  draftBody?: string;
  structureMemo?: string;
  slidesSummary?: string;
  combination?: string;
}

export interface ReviewFormData {
  theme: string;
  draftBody: string;
  structureMemo: string;
  slidesSummary: string;
}

export function validateReviewForm(data: ReviewFormData): ValidationErrors {
  const errors: ValidationErrors = {};

  const theme = data.theme.trim();
  const draft = data.draftBody.trim();
  const memo = data.structureMemo.trim();
  const slides = data.slidesSummary.trim();

  if (theme.length === 0) {
    errors.theme = "テーマは必須です。";
  } else if (theme.length > THEME_MAX_CHARS) {
    errors.theme = `テーマは ${THEME_MAX_CHARS.toLocaleString()} 文字以下にしてください。`;
  }

  if (draft.length > MANUSCRIPT_BLOCK_MAX_CHARS) {
    errors.draftBody = `原稿本文は ${MANUSCRIPT_BLOCK_MAX_CHARS.toLocaleString()} 文字以下にしてください。`;
  }
  if (memo.length > MANUSCRIPT_BLOCK_MAX_CHARS) {
    errors.structureMemo = `構成メモは ${MANUSCRIPT_BLOCK_MAX_CHARS.toLocaleString()} 文字以下にしてください。`;
  }
  if (slides.length > MANUSCRIPT_BLOCK_MAX_CHARS) {
    errors.slidesSummary = `スライド要約は ${MANUSCRIPT_BLOCK_MAX_CHARS.toLocaleString()} 文字以下にしてください。`;
  }

  if (!draft && !memo && !slides) {
    errors.combination =
      "原稿本文・構成メモ・スライド要約のうち、少なくとも 1 つを入力してください。";
  }

  const total = theme.length + draft.length + memo.length + slides.length;
  if (total > TOTAL_INPUT_MAX_CHARS) {
    errors.combination =
      errors.combination ??
      `入力合計が ${TOTAL_INPUT_MAX_CHARS.toLocaleString()} 文字を超えています。`;
  }

  return errors;
}

export function hasErrors(errors: ValidationErrors): boolean {
  return Object.keys(errors).length > 0;
}
