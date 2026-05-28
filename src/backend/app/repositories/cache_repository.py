"""Generation cache — pipeline §11.
cache key = genre + mood + prompt + duration + seed.
대상: lyrics / music / image / video.
subtitle/render는 cache 제외.

MVP에서는 in-memory + JSON file 영속화로 충분. production은 Redis 또는 Firestore로 교체.
"""

import hashlib
import json
from pathlib import Path
from typing import Any
from ..core.config import get_settings
from ..core.logger import get_logger

log = get_logger("cache")


def make_cache_key(stage: str, *, genre: str, mood: str, prompt: str, duration: int, seed: int | None = None) -> str:
    raw = json.dumps(
        {"stage": stage, "genre": genre, "mood": mood, "prompt": prompt, "duration": duration, "seed": seed or 0},
        sort_keys=True,
    )
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:24]


class FileCache:
    """간단한 JSON 디스크 캐시."""

    def __init__(self) -> None:
        settings = get_settings()
        self.root = Path(settings.temp_dir).resolve() / "cache"
        self.root.mkdir(parents=True, exist_ok=True)

    def _path(self, key: str) -> Path:
        return self.root / f"{key}.json"

    def get(self, key: str) -> dict[str, Any] | None:
        p = self._path(key)
        if not p.exists():
            return None
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except Exception as e:
            log.warning(f"cache read failed {key}: {e}")
            return None

    def set(self, key: str, value: dict[str, Any]) -> None:
        try:
            self._path(key).write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")
        except Exception as e:
            log.warning(f"cache write failed {key}: {e}")


_cache_singleton: FileCache | None = None


def get_cache() -> FileCache:
    global _cache_singleton
    if _cache_singleton is None:
        _cache_singleton = FileCache()
    return _cache_singleton
