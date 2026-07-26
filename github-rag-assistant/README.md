# Codebase RAG Assistant

Ask natural-language questions about any public GitHub repository and get
answers grounded in the actual source code, with file and line citations.

## Structure

```
backend/            FastAPI service
  app/
    api/routes/     HTTP endpoints (health, repos, query)
    core/           logging, auth placeholder
    services/       github_loader, parser, embeddings, vector_db, retriever, reranker, llm, prompts
    workers/        background indexing job + in-memory job store
    models/         pydantic request/response schemas
    utils/          file filters, hashing
  tests/
  repositories/     cloned repos land here at runtime (gitignored)

frontend/           Next.js UI (repo URL input, question box, answer + citations)

docker-compose.yml  qdrant + backend + frontend
```

## Architecture

```
Repo URL -> clone (GitPython, shallow) -> chunk by function/class (tree-sitter)
  -> embed (dense + sparse) -> Qdrant (per-repo collection)

Question -> hybrid search (dense + sparse, merged via reciprocal rank fusion)
  -> rerank (cross-encoder) -> LLM -> answer with file:line citations
```

Indexing runs as a background task (FastAPI `BackgroundTasks` for now — swap
in Celery, RQ, or Arq once repo size or traffic outgrows a single process).

Re-indexing is meant to become incremental: `github_loader.get_changed_files`
already returns the diff since the last indexed commit; wire that into
`workers/indexing_tasks.py` so re-indexing only re-chunks and re-embeds
changed files instead of the whole repository.

## Running locally (without Docker)

```bash
# backend
cd backend
cp .env.example .env
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload

# frontend (separate terminal)
cd frontend
cp .env.example .env
npm install
npm run dev
```

You'll also need Qdrant running somewhere reachable at `QDRANT_URL` —
easiest is `docker run -p 6333:6333 qdrant/qdrant`.

## Running with Docker

```bash
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
docker compose up --build
```

- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- Qdrant dashboard: http://localhost:6333/dashboard

## Environment variables

See `backend/.env.example` and `frontend/.env.example` for the full list.
Key ones: `EMBEDDING_PROVIDER` (`bge` or `openai`), `LLM_PROVIDER` (`groq` or
`openai`), `QDRANT_URL`.

## Auth

Not enforced yet. `app/core/security.py` and `app/api/deps.py` already wire
a `get_current_user` dependency through every route, so enabling real
JWT/OAuth verification later is a one-file change, not a refactor.

## What's stubbed vs. real

- `parser.py` currently chunks by fixed line blocks; the tree-sitter
  function/class-level parsing is left as a `TODO` per language.
- `reranker.py` and `embeddings.py` assume `BAAI/bge-reranker-v2-m3` and
  `BAAI/bge-m3` are available locally via `FlagEmbedding` — swap in a
  hosted reranker/embedding API if you'd rather not run these locally.
