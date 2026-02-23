# Changelog

All notable changes to this project will be documented in this file.

## [2.0.2] - 2026-02-23

### 🐛 Fixes
- **CLI Initialization:** Resolved `TypeError` and restored correct `argparse` behavior when `log_analyzer.py` is run without arguments, ensuring proper display of usage information and non-zero exit codes on missing arguments.

## [2.0.1] - 2026-02-23

### 🐛 Fixes
- **Error Handling (API Key/Prompt Files):** Ensured the script exits with a non-zero status code on critical errors (e.g., missing API key or prompt files) to improve behavior in automated pipelines.
- **Code Cleanup & Documentation:** Applied high-priority feedback from code review including:
  - Removed unused `import json` from `log_analyzer.py`.
  - Removed in-chunk `sort_values` from `log_analyzer.py`'s `stream_log_dataframes` function.
  - Added explicit input prerequisites to `README.md` and `README.jp.md` clarifying timestamp ordering.

## [2.0.0] - 2026-02-23

### 💥 Breaking Changes
- **CLI Arguments Refactored:** The command-line interface has been significantly refactored for clarity and better programmatic use.
  - The `--file` argument has been renamed to `--input`.
  - The output path is no longer configured in `analysis_config.yaml`. It must now be specified via a new, required `--output` command-line argument.

## [1.0.0] - 2026-02-23

### 🛡️ Security
- **Prompt Injection:** LLMに渡すプロンプトの形式を、指示とデータを完全に分離する方式に変更し、プロンプトインジェクションに対する堅牢性を大幅に向上させました。
- **Path Traversal:** レポートファイルの保存時に、意図しないディレクトリへ書き込みが行われる可能性があったパス・トラバーサルの脆弱性を修正しました。
- **Secret Leakage:** LLM APIとの通信でエラーが発生した際に、詳細なエラーメッセージをログに出力しないように変更し、機密情報が漏洩するリスクを低減しました。

### ✨ Features & Enhancements
- **Progress Bar:** プログレスバーの表示を改善し、巨大なファイルを処理する際に「全体の進捗」と「詳細な進捗」を二重に表示するようにしました。
- **Configuration:** メモリ使用量やトークン上限をより細かく制御するため、以下の設定項目を新たに追加し、テンプレートとドキュメントを更新しました。
    - `analysis_config.yaml`: `dataframe_chunk_size`
    - `system_config.yaml`: `max_summary_tokens`
- **Prompt Generator:** `prompt_generator.py` を、新しい安全なプロンプト形式に対応するように修正しました。
- **Default Settings:** デフォルトのトークンチャンクサイズ (`max_tokens_per_chunk`) を `32768` に更新し、より大きなコンテキストウィンドウを活かせるようにしました。

### 🚀 Performance
- **Memory Usage:** 巨大なログファイルを読み込む際のアーキテクチャを刷新しました。ファイル全体を一度にメモリに読み込むのではなく、ストリーミング形式で少しずつ処理することで、メモリ使用量を劇的に削減しました。

### 🐛 Fixes
- **Error Handling:** 関数内での `exit(1)` の直接呼び出しを廃止し、`main`関数で例外をまとめて捕捉する一貫したエラーハンドリング方式に統一しました。
- **Validation:** 設定ファイル読み込み時に必須項目が欠けていないか検証する処理を追加し、設定ミスによるエラーの発見を容易にしました。
- **`prompt_generator.py`:** 予期せぬエラー発生時に詳細なトレースバックが表示されるように例外処理を改善し、デバッグを容易にしました。
