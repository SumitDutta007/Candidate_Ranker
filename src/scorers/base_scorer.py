"""
Base scorer interface
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Tuple


class BaseScorer(ABC):
    """Abstract base class for all scorers."""

    @abstractmethod
    def score(self, candidate: 'Candidate') -> Tuple[float, Dict[str, Any]]:
        """
        Score a candidate.

        Returns:
            Tuple of (score: float between 0 and 1, details: dict with explanation)
        """
        pass