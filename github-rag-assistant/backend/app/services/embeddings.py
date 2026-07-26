"""Embedding client. Supports BGE-M3 (dense + sparse) or OpenAI (dense only).

Hybrid search needs a sparse signal alongside the dense one. If
EMBEDDING_PROVIDER=openai, Qdrant's native BM25 sparse vectors are used
instead (see services/vector_db.py) so hybrid search still works either way.
"""
from typing import Optional

from app.config import get_settings

settings = get_settings()


class EmbeddingClient:
    def __init__(self):
        self.provider = settings.EMBEDDING_PROVIDER
        self._model = None

    def _load_bge(self):
        if self._model is None:
            from FlagEmbedding import BGEM3FlagModel

            self._model = BGEM3FlagModel(settings.EMBEDDING_MODEL, use_fp16=True)
        return self._model

    def embed_dense(self, texts: list[str]) -> list[list[float]]:
        if self.provider == "bge":
            model = self._load_bge()
            return model.encode(texts, return_dense=True)["dense_vecs"].tolist()
        elif self.provider == "openai":
            from openai import OpenAI

            client = OpenAI(api_key=settings.OPENAI_API_KEY)
            resp = client.embeddings.create(model="text-embedding-3-large", input=texts)
            return [d.embedding for d in resp.data]
        raise ValueError(f"Unknown EMBEDDING_PROVIDER: {self.provider}")

    def embed_sparse(self, texts: list[str]) -> Optional[list[dict]]:
        """Returns {"indices": [...], "values": [...]} per text, or None
        if the provider has no native sparse output (Qdrant's built-in
        BM25 sparse vectors are used instead in that case).
        """
        if self.provider != "bge":
            return None
        model = self._load_bge()
        weights = model.encode(texts, return_sparse=True)["lexical_weights"]
        return [
            {"indices": [int(k) for k in w], "values": [float(v) for v in w.values()]}
            for w in weights
        ]
