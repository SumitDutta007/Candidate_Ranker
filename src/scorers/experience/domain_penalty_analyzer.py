class DomainPenaltyAnalyzer:
    
    CV_TERMS = [
            "computer vision",
            "object detection",
            "segmentation",
            "opencv",
            "yolo",
            "image classification"
        ]
    @staticmethod
    def analyze(candidate):
        text = " ".join(
            [
                exp.get(
                    "description",
                    ""
                )
                for exp in candidate.career_history
            ]
        ).lower()

        cv_hits = sum(
            term in text
            for term in DomainPenaltyAnalyzer.CV_TERMS
        )

        retrieval_hits = sum(
            term in text
            for term in [
                "retrieval",
                "ranking",
                "search",
                "recommendation"
            ]
        )

        if (
            cv_hits >= 2
            and retrieval_hits == 0
        ):
            return {
                "domain_penalty": 0.85
            }
        return {
            "domain_penalty": 1.0
        }