class CandidateRetriever:

    @staticmethod
    def score(candidate_text, terms):

        text = candidate_text.lower()

        score = 0

        for term in terms:
            score += text.count(term)

        return score

    @staticmethod
    def retrieve(candidates, expanded_terms):

        retrieved = []

        for item in candidates:

            candidate_text = item["candidate_text"]

            retrieval_score = (
                CandidateRetriever.score(
                    candidate_text,
                    expanded_terms
                )
            )

            if retrieval_score > 0:

                item["retrieval_score"] = retrieval_score

                retrieved.append(item)

        retrieved.sort(
            key=lambda x: x["retrieval_score"],
            reverse=True
        )

        return retrieved