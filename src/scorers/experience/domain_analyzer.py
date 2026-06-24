class DomainAnalyzer:

    @staticmethod
    def analyze(candidate, jd):
        profile = candidate.profile

        text_parts = [
            profile.get("headline", ""),
            profile.get("summary", ""),
            profile.get("current_title", "")
        ]

        for exp in candidate.career_history:
            text_parts.append(exp.get("title", ""))
            text_parts.append(exp.get("description", ""))

        text = " ".join(text_parts).lower()

        term_counts = {}
        for term in jd.domain_keywords:
            count = text.count(term)

            if count > 0:
                term_counts[term] = count

        matches = set(term_counts.keys())

        domain_score = min(len(matches) / 12.0, 1.0)

        retrieval_experience = any(
            term in matches
            for term in [
                "retrieval",
                "search",
                "semantic search",
                "hybrid search",
                "vector search"
            ]
        )

        ranking_experience = any(
            term in matches
            for term in [
                "ranking",
                "learning to rank",
                "ltr",
                "ndcg",
                "mrr",
                "map"
            ]
        )

        evaluation_experience = any(
            term in matches
            for term in [
                "ndcg",
                "mrr",
                "map",
                "a/b test",
                "ab test",
                "offline evaluation",
                "online evaluation",
                "benchmarking",
                "evaluation framework"
            ]
        )

        recommendation_experience = any(
            term in matches
            for term in [
                "recommendation",
                "recommender",
                "recommendation engine",
                "recommendation system",
            ]
        )

        retrieval_strength = sum(
            term_counts.get(term, 0)
            for term in [
                "retrieval",
                "search",
                "information retrieval",
                "semantic search",
                "vector search",
                "faiss",
                "bm25"
            ]
        )

        ranking_strength = sum(
            term_counts.get(term, 0)
            for term in [
                "ranking",
                "learning to rank",
                "ltr",
                "ndcg",
                "mrr",
                "map"
            ]
        )

        recommendation_strength = sum(
            term_counts.get(term, 0)
            for term in [
                "recommendation",
                "recommender",
                "recommendation engine",
                "recommendation system"
            ]
        )        

        return {
            "domain_score": domain_score,

            "retrieval_experience": retrieval_experience,
            "ranking_experience": ranking_experience,
            "recommendation_experience": recommendation_experience,
            "evaluation_experience": evaluation_experience,

            "retrieval_strength": retrieval_strength,
            "ranking_strength": ranking_strength,
            "recommendation_strength": recommendation_strength,

            "matched_terms": sorted(matches)
        }