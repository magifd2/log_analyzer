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
You are an expert in designing prompts for log analysis tools using the Map-Reduce pattern.
Your task is to create a "Map" prompt (instruction set) that will be used to analyze a chunk of log data.

The final goal of the overall analysis is as follows:
---
{user_objective}
---

Constraints for generating the instruction:
- **System Architecture:** Do NOT include any instructions about how to receive the data (e.g., "Analyze the following log:", placeholders like `{{log_chunk}}`, or XML tags). The system securely isolates the log data using dynamic XML tags and provides it to the LLM automatically.
- **Your Role:** You must ONLY output the core analytical instructions and the required output format. Do not write anything else.
- **Actionable Summary:** Instruct the LLM to compress the log chunk into meaningful "Micro-Summaries" (e.g., user intents, application transitions, workflows, or event sequences) relevant to the final goal. It should not just blindly list factual lines.
- **Format:** The output from this chunk-level analysis will be used as input for a final summarization step, so instruct the LLM to output concise, structured text (e.g., bullet points with timestamps or phases).

Please provide ONLY the text for the chunk analysis instructions, and nothing else.

CHUNK ANALYSIS INSTRUCTIONS:
"""

FINAL_PROMPT_META_TEMPLATE = """
You are an expert in designing prompts for log analysis tools using the Map-Reduce pattern.
Your task is to create a "Reduce" (final summarization) prompt. This will be applied to a chronological series of Micro-Summaries extracted from individual log chunks.

The final goal of the overall analysis is as follows:
---
{user_objective}
---

Constraints for generating the instruction:
- **System Architecture:** Do NOT include any instructions about how to receive the summaries (e.g., placeholders like `{{chunk_summaries}}` or XML tags). The system securely isolates the Micro-Summaries using dynamic XML tags and provides them to the LLM automatically.
- **Your Role:** You must ONLY output the core synthesis instructions and the final report format. Do not write anything else.
- **Synthesis:** Instruct the LLM to connect the dots across the summaries, identifying overarching workflows, intents, root causes, or user personas based strictly on the provided factual summaries.
- **Output Requirements:** Instruct the LLM to output the final report in Japanese, well-structured using Markdown headings and lists, tailored exactly to answer the user's objective.

Please provide ONLY the text for the final summarization instructions, and nothing else.

FINAL SUMMARIZATION INSTRUCTIONS:
"""

def get_objective(args) -> str:
    """
    Gets the analysis objective from standard input or command-line argument.
    Priority is given to standard input.
    """
    MAX_OBJECTIVE_LENGTH = 2000
    objective = ""
    if not os.isatty(sys.stdin.fileno()):
        print("Reading objective from standard input...")
        objective = sys.stdin.read().strip()
    elif args.objective:
        print("Reading objective from --objective argument...")
        objective = args.objective.strip()

    if not objective:
        raise ValueError("Analysis objective is required. Please provide it via standard input or the --objective argument.")

    if len(objective) > MAX_OBJECTIVE_LENGTH:
        raise ValueError(f"Objective is too long ({len(objective)} chars). Max: {MAX_OBJECTIVE_LENGTH}")
        
    return objective

def load_config(config_path: str) -> dict:
    """Loads a YAML configuration file."""
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        raise
    except yaml.YAMLError as e:
        raise yaml.YAMLError(f"Error parsing YAML file '{config_path}': {e}")

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
        # Sometimes the model might still include the headers, strip them if present
        if "CHUNK ANALYSIS INSTRUCTIONS:" in generated_text:
            generated_text = generated_text.split("CHUNK ANALYSIS INSTRUCTIONS:", 1)[1].strip()
        if "CHUNK ANALYSIS PROMPT:" in generated_text:
             generated_text = generated_text.split("CHUNK ANALYSIS PROMPT:", 1)[1].strip()
        if "FINAL SUMMARIZATION INSTRUCTIONS:" in generated_text:
            generated_text = generated_text.split("FINAL SUMMARIZATION INSTRUCTIONS:", 1)[1].strip()
        if "FINAL SUMMARIZATION PROMPT:" in generated_text:
            generated_text = generated_text.split("FINAL SUMMARIZATION PROMPT:", 1)[1].strip()
        return generated_text
    except Exception as e:
        raise Exception(f"Error calling LLM API: {type(e).__name__}")

def save_prompt_to_file(prompt_text: str, output_path: str):
    """Saves the generated prompt text to a file."""
    try:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(prompt_text)
        print(f"Successfully saved prompt to '{output_path}'")
    except IOError as e:
        raise IOError(f"Error writing to file '{output_path}': {e}")

def main():
    """Main function to generate analysis prompts."""
    try:
        load_dotenv()
        parser = argparse.ArgumentParser(
            description="Generate analysis prompts for the log-analyzer tool using an LLM.",
            formatter_class=argparse.RawTextHelpFormatter
        )
        parser.add_argument("--objective", type=str, help="""A clear, natural language description of the analysis goal.
Can also be provided via standard input.""")
        parser.add_argument("--chunk-output", type=str, required=True, help="Path to save the generated chunk analysis prompt.")
        parser.add_argument("--final-output", type=str, required=True, help="Path to save the generated final summary prompt.")
        parser.add_argument("--system-config", type=str, required=True, help="Path to the system configuration file (e.g., system_config.yaml).")
        args = parser.parse_args()

        objective = get_objective(args)
        
        system_config = load_config(args.system_config)
        llm_config = system_config.get("llm", {})
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables.")

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

    except (ValueError, FileNotFoundError, yaml.YAMLError, IOError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()