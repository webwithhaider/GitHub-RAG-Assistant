from fastapi import APIRouter

from app.config import get_settings
from app.services.vector_db import QdrantService

router = APIRouter()
settings = get_settings()


@router.get("")
def health_check():
    qdrant_ok = True
    try:
        QdrantService(settings).ping()
    except Exception:
        qdrant_ok = False

    return {"status": "ok", "qdrant": qdrant_ok}
