# Copyright (c) 2026 MagiFD2
# This software is released under the MIT License, see LICENSE.

import argparse
import sys
import os
import yaml
from dotenv import load_dotenv
from openai import OpenAI

# Meta-prompts: These are the prompts used to ask the LLM to generate other prompts.

CHUNK_PROMPT_META_TEMPLATE = """
You are an expert in designing prompts for log analysis tools.
Your task is to create a prompt that will be used to analyze a small chunk of a larger log file.

The final goal of the overall analysis is as follows:
---
{user_objective}
---

Based on this final goal, create a prompt for the chunk analysis.

Constraints for the chunk analysis prompt:
- It must NOT include any placeholders like `{{log_chunk}}`. The log data will be provided separately to the language model.
- The prompt should be a pure instruction, telling the LLM what to do with the log data it will receive.
- The prompt should instruct the LLM to focus on extracting factual and objective information from the chunk. This could include lists of errors, summaries of specific events, key statistics, or notable warnings.
- The output from this chunk-level analysis will be used as input for a final summarization step, so it should be concise and structured.

Please provide ONLY the text for the chunk analysis prompt, and nothing else.

CHUNK ANALYSIS PROMPT:
"""

FINAL_PROMPT_META_TEMPLATE = """
You are an expert in designing prompts for log analysis tools.
Your task is to create a final summarization prompt. This prompt will be given to an LLM along with a series of summaries from individual log chunks.

The final goal of the overall analysis is as follows:
---
{user_objective}
---

Based on this final goal, create a prompt for the final summarization.

Constraints for the final summarization prompt:
- It must NOT include any placeholders like `{{chunk_summaries}}`. The chunk summaries will be provided separately to the language model.
- The prompt should be a pure instruction, telling the LLM how to synthesize the information from all chunk summaries into a single, high-level report.
- The final report should identify trends, infer root causes, and suggest concrete recommendations or action items, as requested by the user's objective.

Please provide ONLY the text for the final summarization prompt, and nothing else.

FINAL SUMMARIZATION PROMPT:
"""

def get_objective(args) -> str:
    """
    Gets the analysis objective from standard input or command-line argument.
    Priority is given to standard input.
    """
    objective = ""
    if not os.isatty(sys.stdin.fileno()):
        print("Reading objective from standard input...")
        objective = sys.stdin.read().strip()
    elif args.objective:
        print("Reading objective from --objective argument...")
        objective = args.objective.strip()

    if not objective:
        print("Error: Analysis objective is required.", file=sys.stderr)
        print("Please provide it via standard input or the --objective argument.", file=sys.stderr)
        sys.exit(1)
    return objective

def load_config(config_path: str) -> dict:
    """Loads a YAML configuration file."""
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        print(f"Error: Configuration file not found at '{config_path}'", file=sys.stderr)
        sys.exit(1)
    except yaml.YAMLError as e:
        print(f"Error parsing YAML file '{config_path}': {e}", file=sys.stderr)
        sys.exit(1)

def generate_prompt_from_meta(client: OpenAI, meta_prompt: str, model: str) -> str:
    """Sends the meta-prompt to the LLM and returns the generated prompt."""
    print(f"Generating prompt using model: {model}...")
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are an expert prompt designer."},
                {"role": "user", "content": meta_prompt}
            ]
        )
        generated_text = response.choices[0].message.content.strip()
        # Sometimes the model might still include the "CHUNK ANALYSIS PROMPT:" header
        if "CHUNK ANALYSIS PROMPT:" in generated_text:
            generated_text = generated_text.split("CHUNK ANALYSIS PROMPT:", 1)[1].strip()
        if "FINAL SUMMARIZATION PROMPT:" in generated_text:
            generated_text = generated_text.split("FINAL SUMMARIZATION PROMPT:", 1)[1].strip()
        return generated_text
    except Exception as e:
        print(f"Error calling LLM API: {e}", file=sys.stderr)
        sys.exit(1)

def save_prompt_to_file(prompt_text: str, output_path: str):
    """Saves the generated prompt text to a file."""
    try:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(prompt_text)
        print(f"Successfully saved prompt to '{output_path}'")
    except IOError as e:
        print(f"Error writing to file '{output_path}': {e}", file=sys.stderr)
        sys.exit(1)

def main():
    """Main function to generate analysis prompts."""
    load_dotenv()
    parser = argparse.ArgumentParser(
        description="Generate analysis prompts for the log-analyzer tool using an LLM.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument("--objective", type=str, help="A clear, natural language description of the analysis goal.\nCan also be provided via standard input.")
    parser.add_argument("--chunk-output", type=str, required=True, help="Path to save the generated chunk analysis prompt.")
    parser.add_argument("--final-output", type=str, required=True, help="Path to save the generated final summary prompt.")
    parser.add_argument("--system-config", type=str, required=True, help="Path to the system configuration file (e.g., system_config.yaml).")
    args = parser.parse_args()

    objective = get_objective(args)
    
    system_config = load_config(args.system_config)
    llm_config = system_config.get("llm", {})
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY not found in environment variables.", file=sys.stderr)
        sys.exit(1)

    client = OpenAI(api_key=api_key, base_url=llm_config.get("base_url"))
    model = llm_config.get("model")

    # Generate and save chunk prompt
    meta_prompt_for_chunk = CHUNK_PROMPT_META_TEMPLATE.format(user_objective=objective)
    chunk_prompt = generate_prompt_from_meta(client, meta_prompt_for_chunk, model)
    save_prompt_to_file(chunk_prompt, args.chunk_output)
    print("-" * 30)

    # Generate and save final prompt
    meta_prompt_for_final = FINAL_PROMPT_META_TEMPLATE.format(user_objective=objective)
    final_prompt = generate_prompt_from_meta(client, meta_prompt_for_final, model)
    save_prompt_to_file(final_prompt, args.final_output)

if __name__ == "__main__":
    main()
