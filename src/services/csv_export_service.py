# src/services/csv_export_service.py

import pandas as pd


class CsvExportService:

    @staticmethod
    def export(
        results,
        output_path
    ):

        rows = []

        for rank, result in enumerate(
            results,
            start=1
        ):

            rows.append({
                "candidate_id":
                    result.candidate_id,

                "rank":
                    rank,

                "score":
                    result.final_score,

                "reasoning":
                    result.reasoning
            })

        df = pd.DataFrame(rows)

        df.to_csv(
            output_path,
            index=False,
            float_format="%.4f"
        )

        return df