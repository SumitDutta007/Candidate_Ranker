"""
Candidate Dataset Loader
Supports both JSONL and JSON files.
"""

import json
from pathlib import Path
from typing import Iterator, Dict, Any


class CandidateDatasetLoader:
    """Streams candidate records from JSONL or JSON."""

    def __init__(self, file_path: str):
        self.file_path = file_path

    def load(self) -> Iterator[Dict[str, Any]]:
        path = Path(self.file_path)

        with open(path, "r", encoding="utf-8") as f:

            # --------------------------
            # JSON (.json)
            # --------------------------
            if path.suffix.lower() == ".json":

                try:
                    data = json.load(f)

                except json.JSONDecodeError as e:
                    raise ValueError(f"Invalid JSON: {e}")

                if isinstance(data, list):

                    for candidate in data:
                        yield candidate

                elif isinstance(data, dict):

                    yield data

                else:

                    raise ValueError(
                        "JSON file must contain either a candidate object or a list of candidates."
                    )

            # --------------------------
            # JSONL (.jsonl)
            # --------------------------
            else:

                for line_num, line in enumerate(f, 1):

                    line = line.strip()

                    if not line:
                        continue

                    try:
                        yield json.loads(line)

                    except json.JSONDecodeError as e:

                        raise ValueError(
                            f"Invalid JSON on line {line_num}: {e}"
                        )