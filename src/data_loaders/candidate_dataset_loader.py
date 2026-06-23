"""
Candidate Dataset Loader
"""
import json
from typing import Iterator, Dict, Any


class CandidateDatasetLoader:
    """Streams candidate records from a JSONL file."""

    def __init__(self, file_path: str):
        self.file_path = file_path

    def load(self) -> Iterator[Dict[str, Any]]:
        """Yield candidate dictionaries one by one."""
        with open(self.file_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    yield json.loads(line)
                except json.JSONDecodeError as e:
                    raise ValueError(f"Invalid JSON on line {line_num}: {e}")