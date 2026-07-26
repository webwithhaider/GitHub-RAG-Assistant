from fastapi import APIRouter, Depends

from app.api.deps import get_current_user
from app.models.schemas import QueryRequest, QueryResponse
from app.services import llm, reranker, retriever

router = APIRouter()


@router.post("", response_model=QueryResponse)
def ask_question(payload: QueryRequest, user=Depends(get_current_user)):
    candidates = retriever.hybrid_search(
        query=payload.question,
        repo_id=payload.repo_id,
        top_k=20,
    )
    top_chunks = reranker.rerank(payload.question, candidates, top_k=6)
    answer, citations = llm.generate_answer(payload.question, top_chunks)
    return QueryResponse(answer=answer, citations=citations)
