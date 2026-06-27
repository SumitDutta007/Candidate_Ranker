# src/pipeline/reasoning_generator.py

class ReasoningGenerator:

    @staticmethod
    def generate(
        candidate,
        scores,
        skill_matches,
        exp_details,
        signal_details
    ):
        profile = candidate.get('profile', {})

        title = profile.get('current_title', 'Unknown')
        company = profile.get('current_company', 'Unknown')
        years = profile.get('years_of_experience', 0)

        reason_parts = [
            f"{title} at {company} with {years:.1f} years of experience"
        ]

        if skill_matches:
            top_skills = skill_matches[:5]
            reason_parts.append(
                f"matched skills: {', '.join(top_skills)}"
            )
        else:
            reason_parts.append(
                "no clear skill matches to JD"
            )

        if exp_details.get("consulting_only"):
            reason_parts.append(
                "consulting-heavy background"
            )
        else:
            if exp_details.get("is_product"):
                reason_parts.append(
                    "product company background"
                )

            if exp_details.get("is_consulting"):
                reason_parts.append(
                    "consulting experience"
                )

        if exp_details.get("retrieval_experience"):
            reason_parts.append(
            f"strong retrieval experience "
            f"({exp_details.get('retrieval_strength',0)} matching signals)"
        )

        if exp_details.get("ranking_experience"):
            reason_parts.append(
            f"ranking expertise "
            f"({exp_details.get('ranking_strength',0)} signals)"
        )

        if exp_details.get(
            "recommendation_experience"
        ):
            reason_parts.append(
                "recommendation systems experience"
            )
        if exp_details.get(
            "evaluation_experience"
        ):
            reason_parts.append(
                "experience with evaluation metrics/frameworks"
            )

        per_signal = signal_details.get(
            "per_signal",
            {}
        )

        recruiter_response = (
            per_signal
            .get("recruiter_response_rate", {})
            .get("normalized", 0)
        )

        github_score = (
            per_signal
            .get("github_activity_score", {})
            .get("normalized", -1)
        )

        if recruiter_response > 0.7:
            reason_parts.append(
                "high recruiter engagement"
            )
        elif recruiter_response < 0.3:
            reason_parts.append(
                "low recruiter engagement"
            )

        if github_score > 0.5:
            reason_parts.append(
                "active GitHub presence"
            )
        elif github_score <= 0:
            reason_parts.append(
                "minimal GitHub activity"
            )

        total_score = scores.get(
            'final',
            0.0
        )

        if total_score >= 0.9:
            reason_parts.append(
                "exceptional overall fit"
            )
        elif total_score >= 0.8:
            reason_parts.append(
                "strong fit"
            )
        elif total_score >= 0.7:
            reason_parts.append(
                "good fit"
            )
        else:
            reason_parts.append(
                "moderate fit"
            )

        return "; ".join(reason_parts) + "."