import type { EditorOut } from "@/lib/api-client";

interface EditorBlockProps {
  editor: EditorOut;
}

export function EditorBlock({ editor }: EditorBlockProps) {
  return (
    <section
      className="rounded-lg border-l-4 border-indigo-500 bg-indigo-50 shadow-sm overflow-hidden"
      aria-label="編集長の統合"
    >
      <div className="px-5 py-4">
        <h3 className="text-base font-bold text-indigo-900 mb-3">
          編集長の統合
        </h3>

        <div className="space-y-4 text-sm text-gray-800">
          <div>
            <h4 className="font-semibold text-indigo-800 mb-1">統合コメント</h4>
            <p className="whitespace-pre-wrap leading-relaxed">
              {editor.integrated_comment}
            </p>
          </div>

          {editor.priority_fixes.length > 0 && (
            <div>
              <h4 className="font-semibold text-indigo-800 mb-2">優先修正</h4>
              <ol className="space-y-2">
                {editor.priority_fixes.map((fix) => (
                  <li
                    key={fix.rank}
                    className="flex gap-2 items-start"
                  >
                    <span className="inline-flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-indigo-200 text-xs font-bold text-indigo-800">
                      {fix.rank}
                    </span>
                    <span className="leading-snug">{fix.summary}</span>
                  </li>
                ))}
              </ol>
            </div>
          )}

          {editor.deduplication_notes && (
            <div>
              <h4 className="font-semibold text-indigo-800 mb-1">
                重複整理・矛盾解消
              </h4>
              <p className="whitespace-pre-wrap leading-relaxed text-gray-700">
                {editor.deduplication_notes}
              </p>
            </div>
          )}
        </div>
      </div>
    </section>
  );
}
