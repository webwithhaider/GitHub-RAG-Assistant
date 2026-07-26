"""Chunk source files by function/class using tree-sitter, with a
line-based fallback for languages without a grammar wired up yet.
"""
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from app.utils.file_filters import IGNORED_DIRS, SUPPORTED_EXTENSIONS
from app.utils.hashing import hash_content


@dataclass
class CodeChunk:
    file: str
    language: str
    function: Optional[str]
    start_line: int
    end_line: int
    content: str
    content_hash: str


def iter_source_files(repo_path: Path):
    for path in repo_path.rglob("*"):
        if not path.is_file():
            continue
        if any(part in IGNORED_DIRS for part in path.parts):
            continue
        if path.suffix not in SUPPORTED_EXTENSIONS:
            continue
        yield path


def chunk_file(path: Path, repo_path: Path) -> list[CodeChunk]:
    """Chunk a single file.

    TODO: replace the fallback block below with real tree-sitter parsing
    per language, yielding one chunk per function/class/method and
    including its leading docstring/comment plus enclosing signature so
    each chunk reads standalone.
    """
    text = path.read_text(encoding="utf-8", errors="ignore")
    language = SUPPORTED_EXTENSIONS[path.suffix]
    rel_path = str(path.relative_to(repo_path))

    lines = text.splitlines()
    chunk_size = 80
    chunks = []
    for start in range(0, len(lines), chunk_size):
        block = "\n".join(lines[start : start + chunk_size])
        if not block.strip():
            continue
        chunks.append(
            CodeChunk(
                file=rel_path,
                language=language,
                function=None,
                start_line=start + 1,
                end_line=min(start + chunk_size, len(lines)),
                content=block,
                content_hash=hash_content(block),
            )
        )
    return chunks


def chunk_repository(repo_path: Path) -> list[CodeChunk]:
    chunks = []
    for path in iter_source_files(repo_path):
        chunks.extend(chunk_file(path, repo_path))
    return chunks
