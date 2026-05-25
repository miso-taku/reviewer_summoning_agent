import type { ReviewerOut, ReviewItemOut } from "@/lib/api-client";

interface ReviewCardProps {
  reviewer: ReviewerOut;
  review: ReviewItemOut;
  index: number;
}

export function ReviewCard({ reviewer, review, index }: ReviewCardProps) {
  return (
    <article
      className="rounded-lg border border-gray-200 bg-white shadow-sm overflow-hidden"
      aria-label={`${reviewer.display_name}のレビュー`}
    >
      <div className="border-b border-gray-100 bg-gray-50 px-4 py-3">
        <div className="flex items-center gap-2">
          <span className="inline-flex h-6 w-6 items-center justify-center rounded-full bg-indigo-100 text-xs font-bold text-indigo-700">
            {index + 1}
          </span>
          <h3 className="text-sm font-semibold text-gray-900">
            {reviewer.display_name}
          </h3>
        </div>
        <p className="mt-1 text-xs text-gray-500">
          <span className="font-medium">専門:</span> {reviewer.specialty_axis}
        </p>
        <p className="text-xs text-gray-500">
          <span className="font-medium">観点:</span> {reviewer.perspective}
        </p>
      </div>

      <div className="px-4 py-3 space-y-3 text-sm">
        {review.good_points.length > 0 && (
          <section>
            <h4 className="font-medium text-green-700 mb-1">良い点</h4>
            <ul className="list-disc list-inside space-y-0.5 text-gray-700">
              {review.good_points.map((point, i) => (
                <li key={i}>{point}</li>
              ))}
            </ul>
          </section>
        )}

        {review.issues.length > 0 && (
          <section>
            <h4 className="font-medium text-amber-700 mb-1">指摘</h4>
            <ul className="list-disc list-inside space-y-0.5 text-gray-700">
              {review.issues.map((issue, i) => (
                <li key={i}>{issue}</li>
              ))}
            </ul>
          </section>
        )}

        {review.concrete_fixes.length > 0 && (
          <section>
            <h4 className="font-medium text-blue-700 mb-1">具体修正案</h4>
            <ul className="list-disc list-inside space-y-0.5 text-gray-700">
              {review.concrete_fixes.map((fix, i) => (
                <li key={i}>{fix}</li>
              ))}
            </ul>
          </section>
        )}
      </div>
    </article>
  );
}
