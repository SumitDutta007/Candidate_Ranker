# src/models/candidate_score.py

from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class CandidateScore:

    semantic_score: float

    experience_score: float
    skill_score: float
    signal_score: float

    exp_details: Dict[str, Any]
    skill_details: Dict[str, Any]
    signal_details: Dict[str, Any]

    prefilter_score: float = 0.0

    final_score: float = 0.0