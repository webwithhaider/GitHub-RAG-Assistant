"""Orchestrates one repo indexing run: clone -> chunk -> embed -> upsert.

Called via FastAPI BackgroundTasks today; the function body doesn't need
to change when this moves to a real task queue later.
"""
from app.services import github_loader, parser
from app.services.embeddings import EmbeddingClient
from app.services.vector_db import QdrantService
from app.workers.queue import job_manager

embedder = EmbeddingClient()
vector_db = QdrantService()


def run_indexing_job(job_id: str, repo_url: str):
    try:
        job_manager.update_job(job_id, status="cloning")
        repo_id = repo_url.rstrip("/").split("/")[-1]
        if repo_id.endswith(".git"):
            repo_id = repo_id[: -len(".git")]
        repo_path = github_loader.clone_repository(repo_url, repo_id)

        job_manager.update_job(job_id, status="chunking")
        chunks = parser.chunk_repository(repo_path)

        job_manager.update_job(job_id, status="embedding")
        texts = [c.content for c in chunks]
        dense_vectors = embedder.embed_dense(texts)
        sparse_vectors = embedder.embed_sparse(texts)

        job_manager.update_job(job_id, status="storing")
        vector_db.ensure_collection(repo_id, dense_dim=len(dense_vectors[0]))

        from qdrant_client import models

        points = []
        for i, (chunk, dense) in enumerate(zip(chunks, dense_vectors)):
            vectors = {"dense": dense}
            if sparse_vectors:
                vectors["sparse"] = models.SparseVector(**sparse_vectors[i])
            points.append(
                models.PointStruct(
                    id=i,
                    vector=vectors,
                    payload={
                        "file": chunk.file,
                        "language": chunk.language,
                        "function": chunk.function,
                        "start_line": chunk.start_line,
                        "end_line": chunk.end_line,
                        "content": chunk.content,
                        "content_hash": chunk.content_hash,
                    },
                )
            )
        vector_db.upsert_chunks(repo_id, points)

        job_manager.update_job(job_id, status="done", progress=f"{len(chunks)} chunks indexed")
    except Exception as exc:  # noqa: BLE001
        job_manager.update_job(job_id, status="failed", error=str(exc))
