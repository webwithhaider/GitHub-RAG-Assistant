from typing import List, Optional

from pydantic import BaseModel, HttpUrl


class IndexRepoRequest(BaseModel):
    repo_url: HttpUrl


class IndexRepoResponse(BaseModel):
    job_id: str
    status: str


class JobStatusResponse(BaseModel):
    status: str
    progress: Optional[str] = None
    error: Optional[str] = None


class QueryRequest(BaseModel):
    repo_id: str
    question: str


class Citation(BaseModel):
    file: str
    start_line: int
    end_line: int


class QueryResponse(BaseModel):
    answer: str
    citations: List[Citation]
