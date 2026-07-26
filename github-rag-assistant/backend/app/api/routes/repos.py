import uuid

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException

from app.api.deps import get_current_user
from app.models.schemas import IndexRepoRequest, IndexRepoResponse, JobStatusResponse
from app.workers.indexing_tasks import run_indexing_job
from app.workers.queue import job_manager

router = APIRouter()


@router.post("/index", response_model=IndexRepoResponse)
def index_repo(
    payload: IndexRepoRequest,
    background_tasks: BackgroundTasks,
    user=Depends(get_current_user),
):
    """Kick off (re-)indexing of a repository in the background.

    Uses FastAPI's BackgroundTasks to start. Swap for Celery/RQ/Arq once
    repos or traffic outgrow a single-process worker.
    """
    job_id = str(uuid.uuid4())
    job_manager.create_job(job_id)
    background_tasks.add_task(run_indexing_job, job_id, str(payload.repo_url))
    return IndexRepoResponse(job_id=job_id, status="queued")


@router.get("/index/{job_id}", response_model=JobStatusResponse)
def get_index_status(job_id: str, user=Depends(get_current_user)):
    job = job_manager.get_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return JobStatusResponse(**job)
