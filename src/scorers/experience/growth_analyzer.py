class GrowthAnalyzer:
    @staticmethod
    def analyze(
        candidate
    ):

        levels = {
            "intern": 1,
            "engineer": 2,
            "senior": 3,
            "staff": 4,
            "principal": 5,
            "lead": 5,
            "director": 6
        }

        titles = [
            job.get("title", "").lower()
            for job in candidate.career_history
        ]

        scores = []

        for title in titles:

            level = 0

            for keyword, value in levels.items():

                if keyword in title:
                    level = max(level, value)

            scores.append(level)

        if len(scores) < 2:
            return{
                "growth_score": 0.5
            }
        growth = max(scores) - min(scores)

        return {
            "growth_score": min(growth / 4.0, 1.0)
        }