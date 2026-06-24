from src.utils.text_preprocessing import preprocess_text

class CandidateTextBuilder:

    @staticmethod
    def build(candidate):

        career_history = sorted(
            candidate.career_history,
            key=lambda x: x.get("start_date", ""),
            reverse=True
        )

        skills_text = " ".join(
            f"{skill.get('name','')} {skill.get('proficiency','')}"
            for skill in candidate.skills[:15]
        )

        titles = " ".join(
            exp.get("title", "")
            for exp in career_history[:3]
        )

        descriptions = " ".join(
            exp.get("description", "")[:100]
            for exp in career_history[:3]
        )

        summary = candidate.profile.get(
            "summary",
            ""
        )[:50]

        return preprocess_text(
            candidate.profile.get(
                "current_title",
                ""
            )
            + " "
            + candidate.profile.get(
                "headline",
                ""
            )
            + " "
            + summary
            + " "
            + titles
            + " "
            + skills_text
            + " "
            + descriptions
        )