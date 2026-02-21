# ログ分析ツール (Log Analyzer)

このツールは、大規模なログファイル（JSONLまたはJSON配列形式）をLLM（大規模言語モデル）を使って分析するためのCLI（コマンドラインインターフェース）ツールです。
タイムスタンプに基づいてデータを複数のチャンクに分割することで、LLMのコンテキストウィンドウを超えるサイズのログファイルを扱うことができます。

このツールは、以下の思想に基づいて明確な関心事の分離をしています:
- **システム設定 (`system_config.yaml`):** LLMのエンドポイントやモデル名など、実行環境に依存する設定を定義します。
- **分析設定 (`analysis_config.yaml`):** プロンプトのパスや出力形式など、特定の分析タスクのパラメータを定義します。
- **コマンドライン引数:** 分析対象のログファイルや設定ファイルなど、実行時に主要な入力を提供します。
- **環境変数 (`.env`):** APIキーのような機密情報を格納します。

## ツールの使い方

### 1. 初回セットアップ
まず、Pythonの仮想環境を作成し、必要なライブラリをインストールします。
```bash
# 仮想環境を作成
uv venv

# requirements.txt から依存ライブラリをインストール
uv pip install -r requirements.txt 
```

### 2. 設定ファイルの準備
次に、テンプレートを元に3つの設定ファイルを作成する必要があります。

**A. システム設定**
このファイルは、接続先のLLMを指定します。テンプレートをコピーし、ご自身の環境に合わせて編集してください。このファイルは通常、バージョン管理（Gitなど）に含めるべきではありません。
```bash
cp system_config.yaml.template system_config.yaml
# system_config.yaml を編集し、base_url や model などを設定します
```

**B. 分析設定**
このファイルは、データ分析の方法を定義します。分析タスクごとに異なる設定ファイルを作成することも可能です。
```bash
cp analysis_config.yaml.template analysis_config.yaml
# 必要に応じて analysis_config.yaml を編集し、プロンプトのパスや出力ファイル名を変更します
```

**C. APIキー**
機密情報であるAPIキーは `.env` ファイルに格納します。このファイルはGitによって無視されます。
```bash
cp .env.template .env
# .env ファイルを編集し、ご自身の OPENAI_API_KEY を設定します
```

### 3. 分析の実行
ツールを実行するには、分析対象のログファイルと2つの設定ファイルをコマンドライン引数として渡す必要があります。

*   **実行コマンドの例:**
    ```bash
    # まず仮想環境を有効化
    source .venv/bin/activate
    
    # 分析を実行
    python log_analyzer.py 
      --file data/large_sample.jsonl 
      --system-config system_config.yaml 
      --analysis-config analysis_config.yaml
    ```
*   **仮想環境を有効化しない場合:**
    ```bash
    ./.venv/bin/python3 log_analyzer.py 
      --file data/large_sample.jsonl 
      --system-config system_config.yaml 
      --analysis-config analysis_config.yaml
    ```

### 4. 結果の確認
分析レポートは、`analysis_config.yaml` で指定された `output/` ディレクトリ内に保存されます。

## プロジェクト構成
```
log_analyzer/
├── .venv/                      # Python 仮想環境
├── data/                       # 入力ログファイル用ディレクトリ
│   ├── sample.jsonl
│   └── large_sample.jsonl
├── output/                     # 分析レポート用ディレクトリ
├── prompts/                    # プロンプトテンプレート用ディレクトリ
│   ├── summarize_all.txt
│   └── summarize_chunk.txt
├── .env                        # ローカル環境変数 (APIキー)
├── .env.template
├── .gitignore
├── analysis_config.yaml        # 分析設定ファイル
├── analysis_config.yaml.template
├── create_dummy_logs.py        # テストデータ生成スクリプト
├── log_analyzer.py                     # メインアプリケーション
├── prompt_generator.py         # プロンプト生成補助ツール
├── README.md                   # 英語版README
├── README.jp.md                # 日本語版README
├── requirements.txt
├── system_config.yaml          # システム設定ファイル
├── system_config.yaml.template
└── validate_jsonl.py           # JSONLファイル検証ユーティリティ
```

## 補助ツール: プロンプトジェネレーター

新しい分析プロンプトを簡単に作成するために、`prompt_generator.py` スクリプトを利用できます。このツールは、あなたが与えた一つの大まかな「分析目的」に基づいて、`log_analyzer.py` が必要とする2種類のプロンプトファイル（チャンク用と最終用）をLLMを使って自動生成します。

### プロンプトジェネレーターの使い方

分析目的は、コマンドライン引数または標準入力で与えることができます。

**方法A: `--objective` 引数を使う**
```bash
python prompt_generator.py 
  --objective "すべてのCRITICALエラーを見つけ出し、解決策を提案してください。" 
  --chunk-output "prompts/chunk_error_analysis.txt" 
  --final-output "prompts/final_error_report.txt" 
  --system-config "system_config.yaml"
```

**方法B: 標準入力を使う（長い分析目的に便利です）**
```bash
echo "システム全体の安定性を評価し、あらゆる重大なエラーの根本原因を特定し、推奨される対策を含む詳細なレポートを作成してください。" | python prompt_generator.py 
  --chunk-output "prompts/chunk_stability_analysis.txt" 
  --final-output "prompts/final_stability_report.txt" 
  --system-config "system_config.yaml"
```

### 生成されたプロンプトの使い方

ジェネレーターを実行すると、2つの新しいプロンプトファイルが作成されます。これらを使うには、`analysis_config.yaml` を更新するだけです。

```yaml
# analysis_config.yaml

prompts:
  # チャンク分析用のプロンプトパス
  chunk_analysis_prompt_path: "prompts/chunk_stability_analysis.txt"
  # 最終要約用のプロンプトパス
  final_summary_prompt_path: "prompts/final_stability_report.txt"
```
これで、この分析設定ファイルを使って `log_analyzer.py` を実行すると、新しく生成されたカスタムプロンプトが使用されます。
