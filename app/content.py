from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CONTENT_PATH = PROJECT_ROOT / "content" / "content.yaml"


@lru_cache(maxsize=4)
def _load_content_cached(path_str: str) -> dict[str, Any]:
    path = Path(path_str)
    if not path.exists():
        raise FileNotFoundError(f"Content file not found: {path}")

    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}

    if not isinstance(data, dict):
        raise ValueError("content.yaml must contain a top-level mapping")

    return data


def load_content(path: Path | str | None = None) -> dict[str, Any]:
    target = Path(path) if path else DEFAULT_CONTENT_PATH
    return _load_content_cached(str(target.resolve()))


def clear_content_cache() -> None:
    _load_content_cached.cache_clear()
