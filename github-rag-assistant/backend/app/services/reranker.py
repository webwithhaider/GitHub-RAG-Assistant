"""Cross-encoder reranking of hybrid search candidates."""
from app.config import get_settings

settings = get_settings()
_model = None


def _load_model():
    global _model
    if _model is None:
        from FlagEmbedding import FlagReranker

        _model = FlagReranker(settings.RERANKER_MODEL, use_fp16=True)
    return _model


def rerank(query: str, candidates: list[dict], top_k: int = 6) -> list[dict]:
    if not candidates:
        return []
    model = _load_model()
    pairs = [[query, c["content"]] for c in candidates]
    scores = model.compute_score(pairs)
    ranked = sorted(zip(candidates, scores), key=lambda pair: pair[1], reverse=True)
    return [c for c, _ in ranked[:top_k]]
