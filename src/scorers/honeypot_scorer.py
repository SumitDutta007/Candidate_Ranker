class HoneypotScorer:

    def score(
        self,
        candidate,
        signal_details
    ):

        risk = 0

        years = candidate.profile.get(
            "years_of_experience",
            0
        )

        title = candidate.profile.get(
            "current_title",
            ""
        ).lower()

        skills = candidate.skills

        career_history = candidate.career_history


        if years < 4 and (
            "staff" in title or
            "principal" in title or
            "director" in title
        ):
            risk += 0.40


        if years < 2 and len(skills) > 25:
            risk += 0.25


        if years > 15 and (
            "junior" in title or
            "intern" in title
        ):
            risk += 0.30


        if len(career_history) > 0:

            total_months = sum(
                exp.get(
                    "duration_months",
                    0
                )
                for exp in career_history
            )

            if total_months / 12 > years + 3:
                risk += 0.30


        github = signal_details.get(
            "github_activity_score",
            0
        )

        recruiter = signal_details.get(
            "recruiter_response_rate",
            0
        )

        if github > 0.95 and recruiter > 0.95:
            risk += 0.20

        return min(risk, 1.0)