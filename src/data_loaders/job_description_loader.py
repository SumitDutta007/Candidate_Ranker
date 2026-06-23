"""
Job Description Loader
"""
from typing import Optional


class JobDescriptionLoader:
    """Loads job description text from a file."""

    def __init__(self, file_path: str):
        self.file_path = file_path

    def load(self) -> str:
        """Load and return the job description text."""
        with open(self.file_path, 'r', encoding='utf-8') as f:
            return f.read()