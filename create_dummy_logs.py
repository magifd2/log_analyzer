# Copyright (c) 2026 MagiFD2
# This software is released under the MIT License, see LICENSE.

import argparse
import json
import random
from datetime import datetime, timedelta, timezone

def create_dummy_logs(num_rows: int, output_path: str, template_path: str):
    """
    Generates a large dummy log file in JSONL format.
    """
    # Load message templates from the existing sample file
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            templates = [json.loads(line) for line in f]
    except FileNotFoundError:
        print(f"Error: Template file '{template_path}' not found.")
        print("Creating a default template.")
        templates = [
            {"level": "INFO", "message": "Default message: operation successful."},
            {"level": "ERROR", "message": "Default message: operation failed."}
        ]


    end_time = datetime.now(timezone.utc)
    start_time = end_time - timedelta(seconds=num_rows)

    print(f"Generating {num_rows} log entries from {start_time.isoformat()} to {end_time.isoformat()}...")

    with open(output_path, 'w', encoding='utf-8') as f:
        for i in range(num_rows):
            # Choose a random template
            log_entry = random.choice(templates).copy()
            
            # Create a new timestamp
            log_entry['timestamp'] = (start_time + timedelta(seconds=i)).isoformat()
            
            # To make logs slightly different
            if "message" in log_entry and "#" in log_entry["message"]:
                 log_entry["message"] = log_entry["message"].replace("#1234", f"#{1234 + i}")

            f.write(f"{json.dumps(log_entry)}\n")
            
    print(f"Successfully generated '{output_path}' with {num_rows} lines.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate a large dummy log file.")
    parser.add_argument(
        "--rows",
        type=int,
        default=1000,
        help="Number of log rows to generate."
    )
    parser.add_argument(
        "--output",
        type=str,
        default="data/large_sample.jsonl",
        help="Path to the output log file."
    )
    parser.add_argument(
        "--template",
        type=str,
        default="data/sample.jsonl",
        help="Path to the template log file to source messages from."
    )
    args = parser.parse_args()

    create_dummy_logs(num_rows=args.rows, output_path=args.output, template_path=args.template)
