# src/pipeline/final_ranker.py
class FinalRanker:

    @staticmethod
    def score(
        semantic_score,
        exp_score,
        skill_score,
        signal_score,
        exp_details,
        honeypot_risk
    ):

        base_score = (
            0.35 * semantic_score
            + 0.30 * exp_score
            + 0.10 * skill_score
            + 0.20 * signal_score
        )

        bonus = 0

        if exp_details.get("retrieval_experience"):
            bonus += 0.03

        if exp_details.get("ranking_experience"):
            bonus += 0.03

        if exp_details.get("recommendation_experience"):
            bonus += 0.03

        final_score = min(
            1.0,
            base_score + bonus
        )

        if exp_details.get("consulting_only"):
            final_score *= 0.60

        final_score *= (
            1 - honeypot_risk * 0.40
        )

        return final_score