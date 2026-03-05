# Changelog

All notable changes to this project will be documented in this file.

## [2.4.0] - 2026-03-04

### ✨ Features & Enhancements
- **Improved Prompt Generation:** Significantly enhanced the meta-prompts in `prompt_generator.py`. The generator now produces much more versatile and higher-quality analysis instructions, focusing on extracting meaningful patterns (like user intents and workflows) rather than just factual errors. This improves the overall quality and relevance of the final analysis report.

## [2.3.1] - 2026-03-04

### 📝 Documentation
- Clarified the usage of the `generation_params` in `system_config.yaml.template` and READMEs. Added a strong warning that parameter names must exactly match those supported by the target API endpoint to prevent errors. Provided a comprehensive list of common, standard parameters as examples.

## [2.3.0] - 2026-03-04

### ✨ Features & Enhancements
- **Configurable LLM Parameters:** Users can now specify custom LLM generation parameters (e.g., `temperature`, `top_p`) in a new `generation_params` section within `system_config.yaml`. These parameters are passed directly to the API, allowing for finer control over the model's output.

## [2.2.0] - 2026-03-04

### ✨ Features & Enhancements
- **Configurable Token Estimation:** The character-to-token estimation ratio is now configurable via the `chars_per_token_estimate` parameter in `system_config.yaml`. This allows users to tune the token estimation logic for different languages to avoid token limit errors.

### 🛡️ Security
- **Randomized Tag Injection Hardening:** Enhanced prompt injection protection by using randomized tags (e.g., `<log_data_f9b3a1>`) for data wrapping in both chunk analysis and final summarization. This prevents attackers from guessing and escaping the data fences.

## [2.1.3] - 2026-03-04

### ✨ Features & Enhancements
- **Configurable Token Estimation:** The character-to-token estimation ratio is now configurable via the `chars_per_token_estimate` parameter in `system_config.yaml`. This allows users to tune the token estimation logic for different languages (e.g., English vs. Japanese) to avoid `400 Token Limit Exceeded` errors with non-English log data.

## [2.1.3] - 2026-03-04

### 🛡️ Security
- **First-Order Prompt Injection Hardening:** Hardened the initial chunk analysis step (`analyze_chunk`) against prompt injection from raw log data. Log data is now wrapped in `<log_data>` tags and the system prompt instructs the LLM to treat it as untrusted data.

## [2.1.2] - 2026-03-04

### 🛡️ Security
- **Second-Order Prompt Injection Hardening:** Hardened the final summarization step against second-order prompt injection. Chunk summaries are now wrapped in `<report>` tags and the final summarization prompt explicitly instructs the LLM to treat them as untrusted data, preventing instructions in chunk summaries from being executed.

## [2.1.1] - 2026-03-04

### 🐛 Fixes
- **Unified Error Handling:** Refactored the `summarize_results` function to include the same retry logic as `analyze_chunk`. The main exception handler now correctly catches `APIError` from both functions, ensuring consistent, robust error handling across the entire analysis pipeline.
- **Dependency Pinning:** Pinned the version for the `backoff` library in `requirements.txt` to ensure reproducible builds.

## [2.1.0] - 2026-03-04

### ✨ Features & Enhancements
- **API Call Retries:** Implemented an exponential backoff retry mechanism for API calls using the `backoff` library. This makes the analysis more resilient to transient network issues or temporary API unavailability.

### 🐛 Fixes
- **Halt on Chunk Error:** The analysis process will now halt immediately if a chunk analysis fails after all retries. This prevents the generation of an incomplete or misleading final report.

### Dependencies
- Added `backoff` library to `requirements.txt`.

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
