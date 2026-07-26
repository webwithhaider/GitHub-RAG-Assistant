"""Qdrant wrapper: one collection per indexed repo, with dense + sparse
named vectors so hybrid search doesn't need a second search system.
"""
from qdrant_client import QdrantClient, models

from app.config import get_settings

settings = get_settings()


class QdrantService:
    def __init__(self, cfg=settings):
        self.client = QdrantClient(url=cfg.QDRANT_URL, api_key=cfg.QDRANT_API_KEY)
        self.prefix = cfg.QDRANT_COLLECTION_PREFIX

    def ping(self):
        self.client.get_collections()

    def collection_name(self, repo_id: str) -> str:
        return f"{self.prefix}{repo_id}"

    def ensure_collection(self, repo_id: str, dense_dim: int):
        name = self.collection_name(repo_id)
        if self.client.collection_exists(name):
            return
        self.client.create_collection(
            collection_name=name,
            vectors_config={
                "dense": models.VectorParams(size=dense_dim, distance=models.Distance.COSINE),
            },
            sparse_vectors_config={
                "sparse": models.SparseVectorParams(modifier=models.Modifier.IDF),
            },
        )

    def upsert_chunks(self, repo_id: str, points: list):
        self.client.upsert(collection_name=self.collection_name(repo_id), points=points)

    def delete_by_file(self, repo_id: str, file_path: str):
        self.client.delete(
            collection_name=self.collection_name(repo_id),
            points_selector=models.FilterSelector(
                filter=models.Filter(
                    must=[models.FieldCondition(key="file", match=models.MatchValue(value=file_path))]
                )
            ),
        )

    def search_dense(self, repo_id: str, vector: list[float], top_k: int):
        return self.client.query_points(
            collection_name=self.collection_name(repo_id),
            query=vector,
            using="dense",
            limit=top_k,
        ).points

    def search_sparse(self, repo_id: str, sparse: dict, top_k: int):
        return self.client.query_points(
            collection_name=self.collection_name(repo_id),
            query=models.SparseVector(indices=sparse["indices"], values=sparse["values"]),
            using="sparse",
            limit=top_k,
        ).points
