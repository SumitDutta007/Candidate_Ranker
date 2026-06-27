# src/pipeline/semantic_ranker.py

import numpy as np
from tqdm import tqdm

class SemanticRanker:

    def __init__(self, model):
        self.model = model

    def compute_scores(
        self,
        candidate_texts,
        jd_embedding
    ):

        batch_size = 1024

        embeddings = []

        for i in tqdm(
            range(
                0,
                len(candidate_texts),
                batch_size
            ),
            desc="Computing embeddings"
        ):

            batch = candidate_texts[
                i:i+batch_size
            ]

            batch_emb = self.model.encode(
                batch,
                show_progress_bar=False,
                batch_size=512,
                convert_to_numpy=True,
                normalize_embeddings=True
            )

            embeddings.append(
                batch_emb
            )
        if not embeddings:
            return np.array([])
        
        embeddings = np.vstack(
            embeddings
        )

        profile_scores = (
            embeddings @ jd_embedding
        )

        semantic_scores = np.clip(
            (profile_scores + 1.0) / 2.0,
            0.0,
            1.0
        )

        return semantic_scores