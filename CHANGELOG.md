# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased] - 2026-02-23

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
