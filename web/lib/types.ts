import type { ReviewSuccessResponse } from "./api-client";

export type AppState =
  | { kind: "idle" }
  | { kind: "loading"; startedAt: number }
  | { kind: "result"; data: ReviewSuccessResponse }
  | { kind: "error"; message: string };
