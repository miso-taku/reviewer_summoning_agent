import type { ReviewSuccessResponse } from "@/lib/api-client";
import { ReviewCard } from "./ReviewCard";
import { EditorBlock } from "./EditorBlock";

interface ResultSectionProps {
  data: ReviewSuccessResponse;
}

export function ResultSection({ data }: ResultSectionProps) {
  return (
    <div className="space-y-6">
      <h2 className="text-lg font-bold text-gray-900">レビュー結果</h2>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {data.reviewers.map((reviewer, i) => {
          const review = data.reviews.find(
            (r) => r.reviewer_id === reviewer.id
          );
          if (!review) return null;
          return (
            <ReviewCard
              key={reviewer.id}
              reviewer={reviewer}
              review={review}
              index={i}
            />
          );
        })}
      </div>

      <EditorBlock editor={data.editor} />
    </div>
  );
}
