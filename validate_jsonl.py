# Copyright (c) 2026 MagiFD2
# This software is released under the MIT License, see LICENSE.

import json
import argparse

def validate_jsonl(file_path: str):
    """
    Validates each line of a JSONL file to ensure it's a valid JSON object.
    """
    print(f"Validating '{file_path}'...")
    with open(file_path, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f, 1):
            # Skip empty lines
            if not line.strip():
                continue
            try:
                json.loads(line)
            except json.JSONDecodeError as e:
                print(f"Error on line {i}: {e}")
                print(f"Content: {line.strip()}")
                print("-" * 20)
    print("Validation complete.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Validate a JSONL file.")
    parser.add_argument(
        "file",
        type=str,
        help="Path to the JSONL file to validate."
    )
    args = parser.parse_args()
    validate_jsonl(args.file)
