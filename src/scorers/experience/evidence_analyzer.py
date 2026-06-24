import re

class EvidenceAnalyzer:

    EVIDENCE_VERBS = [
        "built",
        "designed",
        "implemented",
        "developed",
        "created",
        "deployed",
        "optimized",
        "improved",
        "owned",
        "led",
        "architected",
        "reduced",
        "increased",
        "improved",
        "optimized"
    ]

    @staticmethod
    def analyze(candidate):
        evidence_score = 0

        keywords = [
            "retrieval",
            "search",
            "ranking",
            "recommendation",
            "ndcg",
            "mrr",
            "learning to rank",
            "ltr",
            "bm25",
            "faiss",
            "embeddings",
            "vector search"
        ]
        METRIC_PATTERNS = [
            "%",
            "latency",
            "throughput",
            "accuracy",
            "ndcg",
            "mrr"
        ]

        for exp in candidate.career_history:

            desc = (
                exp.get(
                    "description",
                    ""
                ).lower()
            )

            for verb in EvidenceAnalyzer.EVIDENCE_VERBS:

                for keyword in keywords:

                    pattern = (
                        f"{verb}.*{keyword}"
                    )

                    if re.search(
                        pattern,
                        desc
                    ):
                        evidence_score += 1

        for exp in candidate.career_history:
            desc = exp.get(
                "description",
                ""
            ).lower()

            metric_hits = sum(
                pattern in desc
                for pattern in METRIC_PATTERNS
            )

            evidence_score += (
                metric_hits * 0.5
            )

        return {
            "evidence_score" : min(evidence_score / 10.0,1.0)
        }