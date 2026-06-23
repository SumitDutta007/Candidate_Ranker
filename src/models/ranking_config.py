# src/models/ranking_config.py

from dataclasses import dataclass


@dataclass
class RankingConfig:

    TOP_SEMANTIC_POOL: int = 5000

    SEMANTIC_WEIGHT: float = 0.50

    EXPERIENCE_WEIGHT: float = 0.25

    SKILL_WEIGHT: float = 0.15

    SIGNAL_WEIGHT: float = 0.10