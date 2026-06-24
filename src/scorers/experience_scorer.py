"""
Experience and pedigree scorer
"""
from typing import Tuple, Dict, Any
from ..utils.scoring_weights import (
    IDEAL_EXP_MIN, IDEAL_EXP_MAX, EXP_RANGE_TOLERANCE
)
from .base_scorer import BaseScorer
from ..models.candidate import Candidate

from .experience.domain_analyzer import DomainAnalyzer
from .experience.evidence_analyzer import EvidenceAnalyzer
from .experience.growth_analyzer import GrowthAnalyzer
from .experience.company_analyzer import CompanyAnalyzer
from .experience.domain_penalty_analyzer import DomainPenaltyAnalyzer


class ExperienceScorer(BaseScorer):
    """Computes experience and pedigree score."""

    def __init__(self, jd):
        self.jd = jd

    def score(self, candidate: Candidate):
        """Return experience score in [0, 1] and details."""
        profile = candidate.profile
        years_exp = profile.get('years_of_experience', 0)

        domain = DomainAnalyzer.analyze(candidate, self.jd)
        if candidate.candidate_id == "CAND_0000001":
            print("\n========== DOMAIN ANALYZER ==========")
            print(domain)
        evidence = EvidenceAnalyzer.analyze(candidate)
        if candidate.candidate_id == "CAND_0000001":
            print("\n========== EVIDENCE ANALYZER ==========")
            print(evidence)
        growth = GrowthAnalyzer.analyze(candidate)
        company = CompanyAnalyzer.analyze(candidate)
        if candidate.candidate_id == "CAND_0000001":
            print("\n========== COMPANY ANALYZER ==========")
            print(company)
        penalty = DomainPenaltyAnalyzer.analyze(candidate)
        
        # Years of experience score: ideal range gets 1.0, linear falloff outside
        target_exp = self.jd.target_experience

        distance = abs(
            years_exp -
            target_exp
        )

        years_score = max(
            0.0,
            1.0 - (
                distance / 10.0
            )
        )
        if years_exp > self.jd.max_experience + 4:
            years_score *= 0.80


        exp_score = (
            0.25 * years_score +
            0.35 * domain["domain_score"] +
            0.05 * company["product_score"] +
            0.20 * evidence["evidence_score"] +
            0.05 * company["consulting_score"] +
            0.10 * growth["growth_score"]
        )
        exp_score *= penalty["domain_penalty"]
        exp_score = max(0.0, min(1.0, exp_score))

        details = {
            "years_of_experience": years_exp,
            "years_score": years_score,

            "is_product": company["is_product"],
            "is_consulting": company["is_consulting"],
            "consulting_only": company["consulting_only"],

            "product_score": company["product_score"],
            "consulting_score": company["consulting_score"],

            "domain_score": domain["domain_score"],
            "evidence_score": evidence["evidence_score"],

            "retrieval_experience": domain["retrieval_experience"],
            "ranking_experience": domain["ranking_experience"],
            "recommendation_experience": domain["recommendation_experience"],
            "evaluation_experience": domain["evaluation_experience"],

            "retrieval_strength": domain["retrieval_strength"],
            "ranking_strength": domain["ranking_strength"],
            "recommendation_strength": domain["recommendation_strength"],

            "matched_domain_terms": domain["matched_terms"],

            "final_experience_score": exp_score
        }
        return exp_score, details