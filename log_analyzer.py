# Copyright (c) 2026 MagiFD2
# This software is released under the MIT License, see LICENSE.

import argparse
import os
import yaml
import pandas as pd
import json
from dotenv import load_dotenv
from openai import OpenAI
from tqdm import tqdm

def load_logs_to_dataframe(file_path: str, timestamp_field: str, timestamp_format: str) -> pd.DataFrame:
    """
    Loads logs from a JSONL file, sorts them by timestamp, and returns a pandas DataFrame.
    """
    try:
        df = pd.read_json(file_path, lines=True)
    except ValueError as e:
        if "Trailing data" in str(e):
            df = pd.read_json(file_path)
        else:
            raise
    except FileNotFoundError:
        print(f"Error: Log file not found at '{file_path}'")
        exit(1)


    if timestamp_field not in df.columns:
        raise ValueError(f"Timestamp field '{timestamp_field}' not found in log file.")

    if timestamp_format == "iso8601":
        df[timestamp_field] = pd.to_datetime(df[timestamp_field])
    elif timestamp_format == "epoch":
        df[timestamp_field] = pd.to_datetime(df[timestamp_field], unit='s')
    else:
        df[timestamp_field] = pd.to_datetime(df[timestamp_field], format=timestamp_format)

    df = df.sort_values(by=timestamp_field).reset_index(drop=True)
    return df

def create_log_chunks(df: pd.DataFrame, max_tokens_per_chunk: int) -> list[str]:
    """
    Creates chunks of log data from a DataFrame, based on an approximate token limit.
    """
    chunks = []
    current_chunk_rows = []
    current_char_count = 0
    char_limit = max_tokens_per_chunk * 3.5

    for _, row in df.iterrows():
        row_json_str = row.to_json(date_format='iso')
        row_char_count = len(row_json_str)

        if current_char_count + row_char_count > char_limit and current_chunk_rows:
            chunks.append("\n".join(current_chunk_rows))
            current_chunk_rows = []
            current_char_count = 0

        current_chunk_rows.append(row_json_str)
        current_char_count += row_char_count

    if current_chunk_rows:
        chunks.append("\n".join(current_chunk_rows))
    return chunks

def analyze_chunk(client: OpenAI, chunk_text: str, prompt_template: str, model: str) -> str:
    """
    Analyzes a single log chunk using the LLM.
    """
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant specialized in log analysis."},
                {"role": "user", "content": prompt_template.format(log_chunk=chunk_text)}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Warning: Error analyzing a chunk: {e}")
        return f"Error analyzing chunk: {e}"

def summarize_results(client: OpenAI, summaries: list[str], prompt_template: str, model: str) -> str:
    """
    Summarizes the collected chunk summaries into a final report.
    """
    full_summary_text = "\n\n---\n\n".join(summaries)
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant specialized in summarizing analysis reports."},
                {"role": "user", "content": prompt_template.format(chunk_summaries=full_summary_text)}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Warning: Error during final summarization: {e}")
        return f"Error during final summarization: {e}"

def load_config(config_path: str) -> dict:
    """Loads a YAML configuration file."""
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        print(f"Error: Configuration file not found at '{config_path}'")
        exit(1)
    except yaml.YAMLError as e:
        print(f"Error parsing YAML file '{config_path}': {e}")
        exit(1)

def main():
    """
    Main function to run the log analysis process.
    """
    load_dotenv()

    parser = argparse.ArgumentParser(
        description="Analyze large log files using LLM.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        "--file",
        type=str,
        required=True,
        help="Path to the log file to be analyzed."
    )
    parser.add_argument(
        "--system-config",
        type=str,
        required=True,
        help="Path to the system configuration file (e.g., system_config.yaml)."
    )
    parser.add_argument(
        "--analysis-config",
        type=str,
        required=True,
        help="Path to the analysis configuration file (e.g., analysis_config.yaml)."
    )
    args = parser.parse_args()

    # --- Load Configurations ---
    print("Loading configurations...")
    system_config = load_config(args.system_config)
    analysis_config = load_config(args.analysis_config)
    print("Configurations loaded successfully.")

    # --- 1. Load log data ---
    data_config = analysis_config.get("data", {})
    print(f"Loading logs from '{args.file}'...")
    df = load_logs_to_dataframe(
        args.file,
        data_config.get("timestamp_field"),
        data_config.get("timestamp_format")
    )
    print(f"Successfully loaded {len(df)} log entries.")

    # --- 2. Chunk data ---
    llm_config = system_config.get("llm", {})
    log_chunks = create_log_chunks(df, llm_config.get("max_tokens_per_chunk", 2048))
    print(f"Created {len(log_chunks)} chunks.")

    # --- 3. Analyze each chunk (Map) ---
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY not found in environment variables.")
        print("Please create a .env file and add your API key to it.")
        return

    client = OpenAI(api_key=api_key, base_url=llm_config.get("base_url"))
    model = llm_config.get("model")
    
    prompts_config = analysis_config.get("prompts", {})
    try:
        with open(prompts_config.get("chunk_analysis_prompt_path"), "r", encoding="utf-8") as f:
            chunk_prompt_template = f.read()
    except FileNotFoundError:
        print(f"Error: Chunk analysis prompt file '{prompts_config.get('chunk_analysis_prompt_path')}' not found.")
        return

    chunk_summaries = []
    print("Analyzing chunks using LLM...")
    for chunk in tqdm(log_chunks, desc="Analyzing Chunks"):
        summary = analyze_chunk(client, chunk, chunk_prompt_template, model)
        chunk_summaries.append(summary)
    print("All chunks analyzed.")

    # --- 4. Summarize results (Reduce) ---
    if chunk_summaries:
        try:
            with open(prompts_config.get("final_summary_prompt_path"), "r", encoding="utf-8") as f:
                final_prompt_template = f.read()
        except FileNotFoundError:
            print(f"Error: Final summary prompt file '{prompts_config.get('final_summary_prompt_path')}' not found.")
            return
            
        print("Generating final report...")
        final_report = summarize_results(client, chunk_summaries, final_prompt_template, model)
        print("Final report generated.")
    else:
        final_report = "No summaries were generated from the log chunks."
        print("Skipping final report generation as there were no chunk summaries.")

    # --- 5. Output final report ---
    output_config = analysis_config.get("output", {})
    output_dir = output_config.get("output_dir", "output")
    report_filename = output_config.get("report_filename", "analysis_report.md")
    
    os.makedirs(output_dir, exist_ok=True)
    report_path = os.path.join(output_dir, report_filename)

    with open(report_path, "w", encoding="utf-8") as f:
        f.write(final_report)

    print(f"\nAnalysis complete. Report saved to '{report_path}'")

if __name__ == "__main__":
    main()
