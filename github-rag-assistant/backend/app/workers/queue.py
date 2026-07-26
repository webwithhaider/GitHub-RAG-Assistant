"""In-memory job tracking to start. Swap for a Redis-backed queue
(Celery/RQ/Arq) once indexing needs to survive a process restart or run
across multiple workers.
"""
from threading import Lock
from typing import Optional


class JobManager:
    def __init__(self):
        self._jobs: dict[str, dict] = {}
        self._lock = Lock()

    def create_job(self, job_id: str):
        with self._lock:
            self._jobs[job_id] = {"status": "queued", "progress": None, "error": None}

    def update_job(self, job_id: str, **fields):
        with self._lock:
            if job_id in self._jobs:
                self._jobs[job_id].update(fields)

    def get_job(self, job_id: str) -> Optional[dict]:
        return self._jobs.get(job_id)


job_manager = JobManager()
