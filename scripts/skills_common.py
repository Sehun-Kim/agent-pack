#!/usr/bin/env python3

from __future__ import annotations

import hashlib
from pathlib import Path


def sha256_tree(root: Path) -> str:
    """Deterministic sha256 over a directory tree.

    Hash input = for each file in sorted(path):
      relpath (POSIX) + NUL + file_bytes + NUL

    - Ignores directories.
    - Treats file contents as raw bytes (no newline normalization).
    """

    if not root.exists():
        raise FileNotFoundError(root)
    if not root.is_dir():
        raise NotADirectoryError(root)

    files: list[Path] = [p for p in root.rglob("*") if p.is_file()]
    files.sort(key=lambda p: p.relative_to(root).as_posix())

    h = hashlib.sha256()
    for p in files:
        rel = p.relative_to(root).as_posix().encode("utf-8")
        h.update(rel)
        h.update(b"\0")
        h.update(p.read_bytes())
        h.update(b"\0")
    return h.hexdigest()
