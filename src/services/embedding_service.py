# src/services/embedding_service.py

from sentence_transformers import SentenceTransformer
import numpy as np


class EmbeddingService:

    def __init__(
        self,
        model_path="./src/models/all-MiniLM-L6-v2"
    ):
        self.model = SentenceTransformer(
            model_path
        )

    def embed_query(
        self,
        text
    ):

        return self.model.encode(
            [text],
            normalize_embeddings=True,
            show_progress_bar=False
        )[0]

    def embed_documents(
        self,
        docs,
        batch_size=256
    ):

        return self.model.encode(
            docs,
            show_progress_bar=False,
            batch_size=batch_size,
            convert_to_numpy=True,
            normalize_embeddings=True
        )