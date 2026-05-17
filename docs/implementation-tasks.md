# 実装タスクリスト — レビュアー召喚 Web

| 項目 | 内容 |
|------|------|
| 文書ID | IMP-2026-001 |
| 版 | 1.0 |
| 根拠 | [requirements.md](./requirements.md)、[functional-design.md](./functional-design.md)、[technical-design.md](./technical-design.md)、[test-plan.md](./test-plan.md)、[計画書](../.cursor/plans/レビュアー召喚web_ba1e7540.plan.md) |
| 進め方 | **TDD（Red → Green → Refactor）**、**DDD 層分離**（domain → application → infrastructure / presentation） |

実装順は **テスト可能な内側（domain）から外側**へ。各タスク完了時に該当チェックを `[x]` に更新すること。

---

## フェーズ 0 — リポジトリ土台

- [x] **0-1** `backend/` に `pyproject.toml` を用意（Python 3.11+、依存: FastAPI、Uvicorn、Pydantic v2、PydanticAI、httpx、pytest、pytest-asyncio 等。版は README で固定）
- [x] **0-2** パッケージ `src/review_summoning/` の空ディレクトリと `__init__.py` を [technical-design.md §6.3](./technical-design.md) のツリーどおり作成
- [x] **0-3** `backend/tests/` を鏡像構成で作成（`domain/` / `application/` / `presentation/` / `integration/`）
- [x] **0-4** `backend/.env.example` に TEC §10.1 の変数（`CORS_ALLOW_ORIGINS`、`OPENAI_API_KEY` または `ANTHROPIC_API_KEY`、`LOG_LEVEL`、任意で `LLM_MODEL_*`）を記載
- [x] **0-5** ルート `README.md` に文書リンク、`uv run pytest` / `uvicorn` 等の起動・テストコマンド案を記載（計画書「ルート README」）

---

## フェーズ 1 — domain（TDD 第 1 波）

[test-plan.md §4.1](./test-plan.md) に準拠。**先に pytest を書き、Red → 実装で Green。**

- [x] **1-1** `Theme` VO：トリム、1〜2000 文字（Unicode スカラ）、空不可（FUN §5.1 / TEC §4.4.2）
- [x] **1-2** `ManuscriptBundle`（または同等）：`draft_body` / `structure_memo` / `slides_summary`、少なくとも 1 ブロック非空、合計 200000 文字以下、各ブロック上限（FUN §5.1）
- [x] **1-3** `ReviewerId` / `RequestId` 等の識別子 VO（TEC §4.4.2）
- [x] **1-4** `domain/ports/` に `ReviewerSummoningPort` / `SingleReviewPort` / `EditorIntegrationPort` の Protocol（または ABC）（TEC §4.4.3）
- [x] **1-5** 召喚・レビュー・編集長用の **ドメイン型**（Pydantic に依存しないデータクラス等）と `domain/exceptions.py` の例外区分（入力 vs 想定外）
- [x] **1-6** `ReviewSession` 集約：レビュアー 3 名確定前の並列レビュー禁止、`reviewer_id` 整合、編集長は 3 レビュー完了後のみ（TEC §4.4.1）

---

## フェーズ 2 — application（TDD 第 2 波）

- [x] **2-1** `RunReviewPipelineUseCase`（ファイル名 `run_review_pipeline.py`）：コマンド入力 → ドメイン VO 検証呼び出し（TEC §4.3 手順 1）
- [x] **2-2** フェイクポート（固定戻り値）を注入し、**召喚 → 3 並列レビュー → 編集長 1 回**の呼び出し順・回数をアサート（test-plan §4.2）
- [x] **2-3** 並列方針：`asyncio.gather` 等。失敗時は TEC §6.2 の採用案（キャンセル or 先頭例外マップ）に合わせたテスト期待値を固定
- [x] **2-4** 全体タイムアウト 170s ラップ（`asyncio.wait_for`）と超過時のドメイン／アプリケーション例外（→ 後続で 504 / `REQUEST_TIMEOUT` に写像）（TEC §9）
- [x] **2-5** `application/mappers/`（必要なら）：ドメイン結果 → presentation 用 DTO 組み立ての純粋マッピング単体テスト

---

## フェーズ 3 — presentation（FastAPI・薄い層）

- [x] **3-1** `presentation/schemas`（または `dto`）に `ReviewRequestBody`、`ReviewerOut`、`ReviewItemOut`、`EditorOut`、`MetaOut`、`ReviewSuccessResponse`、`ErrorBody` / `ErrorEnvelope`（FUN §6 / TEC §5.2〜5.3）
- [x] **3-2** Pydantic 第 1 段バリデーション（型・各フィールドレンジ）と、ユースケース前のドメイン第 2 段（意味的制約）の両方を通す（TEC §5.3）
- [x] **3-3** `POST /api/v1/review` ルータ実装 → `RunReviewPipelineUseCase.execute` 呼び出し（TEC §7.1）
- [x] **3-4** 例外 → HTTP マッピング（422 `VALIDATION_ERROR`、502 `LLM_UPSTREAM_ERROR`、503 `LLM_UNAVAILABLE`、504 `REQUEST_TIMEOUT`、500 `INTERNAL_ERROR`）（FUN §8 / TEC §7.3）
- [x] **3-5** `presentation/main.py`：`CORSMiddleware`（`CORS_ALLOW_ORIGINS`）、アプリ組み立て、`dependencies.py` でユースケース＋実インフラの DI（TEC §8.1）
- [x] **3-6** `presentation` 単体：`TestClient` で LLM 非呼び出し（モック DI）のスキーマ・マッピングテスト（test-plan §3.1 presentation）

---

## フェーズ 4 — infrastructure（PydanticAI）

- [x] **4-1** `infrastructure/config.py`：Settings（API キー、モデル名、ログレベル）（TEC §10）
- [x] **4-2** `pydantic_ai_summoning.py`：`ReviewerSummoningPort` 実装（3 ペルソナ構造化出力）
- [x] **4-3** `pydantic_ai_review.py`：`SingleReviewPort` 実装（構造化レビュー）
- [x] **4-4** `pydantic_ai_editor.py`：`EditorIntegrationPort` 実装（統合コメント・優先修正等）。`priority_fixes` 最大 20 件・各配列上限は TEC §5.2 に従いプロンプトまたは受信後トリム
- [x] **4-5** 各 LLM 呼び出しに個別タイムアウト（httpx / `wait_for`）。プロバイダ 4xx/5xx・パース失敗をドメイン／アプリケーション例外に正規化（TEC §9）
- [x] **4-6** ログ：原稿本文を出さない・デバッグ時マスク（TEC §8.3 / REQ-NF-022）

---

## フェーズ 5 — 結合テスト（IT-API）

[test-plan.md §3.2](./test-plan.md) の ID に沿う。

- [ ] **5-1** **IT-API-01**：依存注入でインフラをスタブ化、`POST /api/v1/review` が 200 で `reviewers`（3）・`reviews`（3）・`editor`・`meta`（FUN §6.1.2 整合）
- [ ] **5-2** **IT-API-02**：422 + `VALIDATION_ERROR`（テーマ空、3 ブロック全非空違反、合計 200000 超過等）
- [ ] **5-3** **IT-API-03**：スタブ遅延 → 504 + `REQUEST_TIMEOUT`
- [ ] **5-4** **IT-API-04**：スタブが例外 → 502 / 503 と `error.code`
- [ ] **5-5** `pytest` マーカー（例: `@pytest.mark.llm_live`）で実 LLM テストを CI から除外する設定を `pyproject.toml` または `pytest.ini` と README に記載（test-plan §6.2）

---

## フェーズ 6 — フロントエンド（`web/`）

- [ ] **6-1** Next.js（App Router）+ TypeScript + Tailwind を `web/` にスキャフォールド（Node 20 LTS または 22 を README に明記）（TEC §11）
- [ ] **6-2** `web/.env.local.example`：`NEXT_PUBLIC_API_BASE_URL`（TEC §10.2）
- [ ] **6-3** `lib/validation.ts`：FUN §5.1 の定数・必須組合せ・合計サイズのクライアント検証（単体テスト推奨）
- [ ] **6-4** `lib/api-client.ts`：`POST`、Base URL、`AbortController` で **180s** タイムアウト（TEC §14）
- [ ] **6-5** 単一ページ UI（FUN §4）：ヘッダ、入力エリア、段階インジケータ（Loading 時の経過時間ベースのハイライト移動）、結果の 3 カード + 編集長ブロック強調（FUN §4.3）
- [ ] **6-6** 状態：`Idle` → `Loading` → `Result` / エラー表示（FUN §7）。422／5xx／ネットワークの UC-03 表示（FUN §3.3）
- [ ] **6-7** アクセシビリティ最小：`aria-label` / `role="alert"` 等（FUN §4.5）

---

## フェーズ 7 — 仕上げ・任意拡張

- [ ] **7-1** ルート `README.md` 更新：バックエンド・フロントの同時起動手順、CORS オリジンと API Base URL の対応関係
- [ ] **7-2** Uvicorn ソケットタイムアウトを 180s 以上にし、アプリ内 170s バジェットが先に効くことを確認（TEC §9.2）
- [ ] **7-3**（任意）OpenAPI のエクスポート方針を決め、必要なら `openapi.json` 取得手順を README に 1 行
- [ ] **7-4**（任意 E2E）Playwright 等で UC-01 主シナリオ 1 本（test-plan §3.3）
- [ ] **7-5** [technical-design.md §16](./technical-design.md) の「次工程チェックリスト」を実装完了時にすべて満たしているか確認

---

## 依存関係（要約）

```text
0 土台 → 1 domain → 2 application（フェイクポート）→ 3 presentation（ユースケース直結）
         ↘ 4 infrastructure 実装 → 5 結合テスト（スタブのまま IT も可、実装後は実アダプタ＋モック HTTP も検討）
6 web は 3 の API 契約が固まれば並行可能（モック JSON で先行 UI も可）
7 は全フェーズ後
```

---

## 改訂履歴

| 版 | 日付 | 変更内容 |
|----|------|----------|
| 1.0 | 2026-05-12 | 初版（設計4文書・計画に基づく実装分解） |
