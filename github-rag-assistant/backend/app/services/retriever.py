"""Hybrid retrieval: merge dense (vector) and sparse (keyword) candidates
before handing off to the reranker.
"""
from app.services.embeddings import EmbeddingClient
from app.services.vector_db import QdrantService

embedder = EmbeddingClient()
vector_db = QdrantService()


def _reciprocal_rank_fusion(*ranked_lists, k: int = 60):
    scores: dict = {}
    payloads: dict = {}
    for ranked in ranked_lists:
        for rank, point in enumerate(ranked):
            scores[point.id] = scores.get(point.id, 0.0) + 1.0 / (k + rank + 1)
            payloads[point.id] = point.payload
    ordered_ids = sorted(scores, key=scores.get, reverse=True)
    return [payloads[i] for i in ordered_ids]


def hybrid_search(query: str, repo_id: str, top_k: int = 20) -> list[dict]:
    dense_vector = embedder.embed_dense([query])[0]
    dense_hits = vector_db.search_dense(repo_id, dense_vector, top_k)

    sparse_vector = embedder.embed_sparse([query])
    if sparse_vector:
        sparse_hits = vector_db.search_sparse(repo_id, sparse_vector[0], top_k)
        return _reciprocal_rank_fusion(dense_hits, sparse_hits)[:top_k]

    return [point.payload for point in dense_hits]
