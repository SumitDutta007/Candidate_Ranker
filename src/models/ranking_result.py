# src/models/ranking_result.py

from dataclasses import dataclass

@dataclass
class RankingResult:
    candidate_id: str
    final_score: float
    reasoning: str