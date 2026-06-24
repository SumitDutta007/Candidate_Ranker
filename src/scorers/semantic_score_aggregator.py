# src/scorers/semantic_score_aggregator.py

class SemanticScoreAggregator:

    @staticmethod
    def aggregate(
        semantic,
        experience,
        skill,
        signal,
        config
    ):

        return (
            config.SEMANTIC_WEIGHT
            * semantic

            + config.EXPERIENCE_WEIGHT
            * experience

            + config.SKILL_WEIGHT
            * skill

            + config.SIGNAL_WEIGHT
            * signal
        )