"""Clone repositories and detect changed files for incremental indexing."""
import subprocess
from pathlib import Path

from git import Repo

from app.config import get_settings

settings = get_settings()


def clone_repository(repo_url: str, repo_id: str) -> Path:
    """Shallow-clone a repo into REPOSITORIES_DIR/<repo_id>, or pull if it
    already exists locally.
    """
    dest = Path(settings.REPOSITORIES_DIR) / repo_id
    if dest.exists():
        Repo(dest).remotes.origin.pull()
    else:
        dest.parent.mkdir(parents=True, exist_ok=True)
        Repo.clone_from(repo_url, dest, depth=1)
    return dest


def get_head_sha(repo_path: Path) -> str:
    return Repo(repo_path).head.commit.hexsha


def get_changed_files(repo_path: Path, since_sha: str) -> list[str]:
    """Files changed since `since_sha`, for incremental re-indexing.

    Only chunks belonging to these files need to be dropped and re-embedded
    on a re-index, instead of the whole repository.
    """
    result = subprocess.run(
        ["git", "diff", "--name-only", since_sha, "HEAD"],
        cwd=repo_path,
        capture_output=True,
        text=True,
        check=True,
    )
    return [line for line in result.stdout.splitlines() if line.strip()]
