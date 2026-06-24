"""
Behavioural signal scorer
"""
import numpy as np
from typing import Tuple, Dict, Any
from .base_scorer import BaseScorer
from ..models.candidate import Candidate
from ..utils.scoring_weights import SIGNAL_WEIGHTS
from datetime import datetime


class SignalScorer(BaseScorer):
    """Combines the behavioural signals into a single 0‑1 score."""

    def score(self, candidate: Candidate) -> Tuple[float, Dict[str, Any]]:
        """Return signal score in [0, 1] and details."""
        raw = candidate.redrob_signals

        total_weight = 0.0
        weighted_sum = 0.0
        per_signal_details = {}

        for name, (weight, normaliser) in SIGNAL_WEIGHTS.items():
            raw_val = raw.get(name)
            if raw_val is None:
                continue
            try:
                norm_val = normaliser(raw_val)
            except Exception:
                continue
            if norm_val is None:
                continue
            weighted_sum += weight * norm_val
            total_weight += abs(weight)
            per_signal_details[name] = {
                'raw': raw_val,
                'normalized': norm_val,
                'weight': weight,
                'contribution': weight * norm_val
            }

        if total_weight == 0.0:
            score = 0.0
        else:
            score = weighted_sum / total_weight
            score = max(0.0, min(1.0, score))

        details = {
            'signal_score': score,
            'per_signal': per_signal_details,
            'total_weight': total_weight,
            'weighted_sum': weighted_sum
        }
        return score, details