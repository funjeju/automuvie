from typing import Protocol
from ...models.domain import Lyrics, AudioMeta, SectionImages, SectionClips


class LyricsProvider(Protocol):
    async def generate(self, *, genre: str, mood: str, prompt: str, duration: int) -> Lyrics: ...


class MusicProvider(Protocol):
    async def generate(self, *, project_id: str, lyrics: Lyrics, genre: str, mood: str, duration: int) -> AudioMeta: ...


class ImageProvider(Protocol):
    async def generate(self, *, project_id: str, lyrics: Lyrics, genre: str, mood: str) -> list[SectionImages]: ...


class VideoProvider(Protocol):
    async def generate(
        self,
        *,
        project_id: str,
        lyrics: Lyrics,
        images: list[SectionImages],
        genre: str,
        mood: str,
    ) -> list[SectionClips]: ...


class SubtitleProvider(Protocol):
    async def generate(self, *, project_id: str, audio_local_path: str, lyrics: Lyrics) -> str:
        """ASS karaoke subtitle string 반환"""
        ...
