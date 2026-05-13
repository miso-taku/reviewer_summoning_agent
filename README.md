# レビュアー召喚 Web

技術ブログ／LT 用の「レビュアー召喚」エージェント。テーマと原稿を入力すると、3 名のレビュアー（仮想ペルソナ）が並列でレビューし、編集長エージェントが統合コメント・優先修正をまとめて返す **ローカル Web アプリ**。

- バックエンド: [FastAPI](https://fastapi.tiangolo.com/) + [PydanticAI](https://ai.pydantic.dev/)（DDD / TDD）
- フロントエンド: [Next.js](https://nextjs.org/) (App Router) + TypeScript + Tailwind CSS

---

## ドキュメント

実装の根拠は次の 4 文書 + 実装タスクリスト。実装中の判断はこれらに揃える。

| 種別 | 文書 |
|------|------|
| 要求定義書 | [docs/requirements.md](docs/requirements.md) |
| 機能設計書 | [docs/functional-design.md](docs/functional-design.md) |
| 技術設計書 | [docs/technical-design.md](docs/technical-design.md) |
| テスト計画書 | [docs/test-plan.md](docs/test-plan.md) |
| 実装タスクリスト | [docs/implementation-tasks.md](docs/implementation-tasks.md) |
| 元の計画書 | [.cursor/plans/レビュアー召喚web_ba1e7540.plan.md](.cursor/plans/レビュアー召喚web_ba1e7540.plan.md) |

---

## ディレクトリ構成

```text
.
├── backend/                # FastAPI + PydanticAI (DDD)
│   ├── pyproject.toml
│   ├── src/review_summoning/
│   │   ├── domain/         # 値オブジェクト・集約・ポート
│   │   ├── application/    # ユースケース
│   │   ├── infrastructure/ # PydanticAI アダプタ・設定
│   │   └── presentation/   # FastAPI ルータ・DTO
│   ├── tests/              # ドメイン鏡像構成 (TDD)
│   └── .env.example
├── web/                    # Next.js + Tailwind（フェーズ 6 で追加）
│   └── .env.local.example
└── docs/                   # 設計 4 文書 + 実装タスク
```

---

## 必要ランタイム

| ランタイム | 推奨版 |
|------------|--------|
| Python | **3.11+**（`asyncio.TaskGroup` 利用） |
| Node.js | **20 LTS** または **22**（フェーズ 6 から） |
| パッケージ管理 | [uv](https://docs.astral.sh/uv/)（推奨）または `pip` |

---

## セットアップ（バックエンド）

`.env` を準備:

```powershell
Copy-Item backend/.env.example backend/.env
# .env を開いて OPENAI_API_KEY または ANTHROPIC_API_KEY を設定
```

依存をインストール（uv 推奨）:

```powershell
cd backend
uv sync --all-extras
# pip 版: python -m venv .venv; .\.venv\Scripts\Activate.ps1; pip install -e ".[dev]"
```

---

## バックエンド起動

開発サーバ（Uvicorn、ホットリロード）:

```powershell
cd backend
uv run uvicorn review_summoning.presentation.main:app --reload --host 127.0.0.1 --port 8000
```

エンドポイント: `POST http://127.0.0.1:8000/api/v1/review`（フェーズ 3 完了後）

---

## テスト

CI 既定（**実 LLM を呼ばない**。`pyproject.toml` の `addopts` で `-m "not llm_live"` を既定化）:

```powershell
cd backend
uv run pytest
```

カバレッジ付き:

```powershell
uv run pytest --cov=review_summoning --cov-report=term-missing
```

実 LLM を含めて実行（要 API キー、コスト注意。手動・夜間用）:

```powershell
uv run pytest -m llm_live
```

---

## フロントエンド（フェーズ 6 以降）

```powershell
cd web
Copy-Item .env.local.example .env.local
# NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8000 を設定
pnpm install   # または npm install
pnpm dev       # http://localhost:3000
```

### CORS と API Base URL の対応

| バックエンド `CORS_ALLOW_ORIGINS` | フロント `NEXT_PUBLIC_API_BASE_URL` |
|----------------------------------|--------------------------------------|
| `http://localhost:3000`（既定）   | `http://127.0.0.1:8000`              |
| 追加ポートを使う場合はカンマで列挙 | 同期させて変更                       |

ローカル運用時、フロント (`localhost:3000`) からバックエンド (`127.0.0.1:8000`) を叩くため、上記の対応が一致していること。

---

## 開発の進め方

実装は [docs/implementation-tasks.md](docs/implementation-tasks.md) のフェーズ順（0 → 7）。各タスク完了時にチェックボックスを `[x]` に更新する。

- **TDD**: pytest でテストを先に書く（Red）→ 最小実装（Green）→ Refactor。
- **DDD**: `domain → application → infrastructure / presentation` の依存方向を厳守。
- **テストレベル**: 単体（domain / application / presentation）と結合（IT-API、スタブ LLM）。詳細は [テスト計画書](docs/test-plan.md) §3。

---

## ライセンス

社内検証用。外部公開ライセンス未定。
