# Log Analyzer

This is a CLI tool to analyze large log files (JSONL or JSON Array) using an LLM.
It chunks the data based on timestamps to handle files larger than the LLM's context window.

This tool is designed with a clear separation of concerns:
- **System Configuration (`system_config.yaml`):** Defines the execution environment (e.g., LLM endpoint, model).
- **Analysis Configuration (`analysis_config.yaml`):** Defines the parameters for a specific analysis task (e.g., prompts, output format).
- **Command-line Arguments:** Provide the main inputs for a run (the log file and the configuration files).
- **Environment Variables (`.env`):** Store sensitive data like API keys.

## How to Use

### 1. Initial Setup
First, create a virtual environment and install the required dependencies.
```bash
# Create a virtual environment
uv venv

# Install dependencies from requirements.txt
uv pip install -r requirements.txt 
```

### 2. Configuration
You need to create three configuration files based on the templates provided.
The templates include comments explaining each parameter. For memory management of very large files, you can adjust `dataframe_chunk_size` in `analysis_config.yaml` and `max_summary_tokens` in `system_config.yaml`.

**A. System Configuration**
This file tells the tool which LLM to connect to. Copy the template and edit it for your environment. This file should generally not be committed to version control.
```bash
cp system_config.yaml.template system_config.yaml
# Now, edit system_config.yaml to set your base_url, model, etc.
```

**B. Analysis Configuration**
This file defines *how* to analyze the data. You can have multiple analysis configs for different tasks.
```bash
cp analysis_config.yaml.template analysis_config.yaml
# Edit analysis_config.yaml if you want to change prompt paths, output names, etc.
```

**C. API Key**
Store your secret API key in a `.env` file. This file is ignored by Git.
```bash
cp .env.template .env
# Now, edit .env and set your OPENAI_API_KEY
```

### 3. Running the Analysis
To run the tool, you must provide the input log file, the desired output path, and the two configuration files as command-line arguments.

*   **Example Command:**
    ```bash
    # Activate the virtual environment first
    source .venv/bin/activate
    
    # Run the analysis
    python log_analyzer.py \
      --input data/large_sample.jsonl \
      --output output/report.md \
      --system-config system_config.yaml \
      --analysis-config analysis_config.yaml
    ```
*   **Directly (without activating):**
    ```bash
    ./.venv/bin/python3 log_analyzer.py \
      --input data/large_sample.jsonl \
      --output output/report.md \
      --system-config system_config.yaml \
      --analysis-config analysis_config.yaml
    ```

### 4. Check the Output
The analysis report will be saved to the path you specified with the `--output` argument.

## Project Structure
```
log_analyzer/
├── .venv/                      # Python virtual environment
├── data/                       # Directory for input log files
│   ├── sample.jsonl
│   └── large_sample.jsonl
├── output/                     # Directory for analysis reports
├── prompts/                    # Directory for prompt templates
│   ├── summarize_all.txt
│   └── summarize_chunk.txt
├── .env                        # Local environment variables (API key)
├── .env.template
├── .gitignore
├── analysis_config.yaml        # Your analysis configuration
├── analysis_config.yaml.template
├── create_dummy_logs.py        # Script to generate test data
├── log_analyzer.py                     # Main application script
├── prompt_generator.py         # Helper to create new prompts
├── README.md
├── requirements.txt
├── system_config.yaml          # Your system configuration
├── system_config.yaml.template
└── validate_jsonl.py           # Utility to validate JSONL files
```

## Helper Tool: Prompt Generator

To facilitate creating new analysis prompts, you can use the `prompt_generator.py` script. This tool uses an LLM to generate the two required prompt files (`chunk` and `final`) based on a single, high-level objective you provide.

### How to Use the Prompt Generator

You can provide your objective via a command-line argument or standard input.

**Option A: Using the `--objective` argument**
```bash
python prompt_generator.py \
  --objective "Find all critical errors and suggest solutions." \
  --chunk-output "prompts/chunk_error_analysis.txt" \
  --final-output "prompts/final_error_report.txt" \
  --system-config "system_config.yaml"
```

**Option B: Using standard input (for longer objectives)**
```bash
echo "Analyze the overall system stability, identify the root causes of any critical errors, and provide a detailed report with recommended actions." | python prompt_generator.py \
  --chunk-output "prompts/chunk_stability_analysis.txt" \
  --final-output "prompts/final_stability_report.txt" \
  --system-config "system_config.yaml"
```

### Using the Generated Prompts

After running the generator, you will have two new prompt files. To use them, simply update your `analysis_config.yaml`:

```yaml
# analysis_config.yaml

prompts:
  # Path to the prompt file for analyzing individual chunks.
  chunk_analysis_prompt_path: "prompts/chunk_stability_analysis.txt"
  # Path to the prompt file for summarizing the results of all chunks.
  final_summary_prompt_path: "prompts/final_stability_report.txt"
```
Now, when you run `log_analyzer.py` with this analysis config, it will use your newly generated, custom prompts.


