import math
import wave
from pathlib import Path
from ...models.domain import AudioMeta, Lyrics
from ...repositories.storage_repository import get_storage_repository
from ...core.config import get_settings
from ...core.logger import get_logger

log = get_logger("music")


def _synthesize_wav(path: Path, duration: float, sample_rate: int = 44100) -> None:
    """간단한 sine sweep wave 생성 (mp3 의존성 없이 audio 분석 가능하게)."""
    n_samples = int(duration * sample_rate)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sample_rate)
        amp = 12000
        frames = bytearray()
        base_freq = 220.0
        for i in range(n_samples):
            t = i / sample_rate
            mod = 1.0 + 0.25 * math.sin(2 * math.pi * 0.1 * t)
            value = int(amp * math.sin(2 * math.pi * base_freq * mod * t))
            frames += value.to_bytes(2, byteorder="little", signed=True)
        w.writeframes(bytes(frames))


class MockMusicProvider:
    """오프라인 개발용. wav를 mp3 컨테이너로 저장하지 않고 .wav로 두되 path만 audio.mp3로 명명한다."""

    async def generate(self, *, project_id: str, lyrics: Lyrics, genre: str, mood: str, duration: int) -> AudioMeta:
        storage = get_storage_repository()
        local = Path(storage.local_path(project_id, "audio", "audio.wav"))
        local.parent.mkdir(parents=True, exist_ok=True)
        _synthesize_wav(local, duration)
        url = storage.upload(project_id, "audio", "audio.wav", str(local))
        return AudioMeta(audioUrl=url, duration=float(duration), sampleRate=44100)


class LyriaMusicProvider:
    """Lyria 3 Pro 호출 자리. credential 부재 시 mock fallback."""

    async def generate(self, *, project_id: str, lyrics: Lyrics, genre: str, mood: str, duration: int) -> AudioMeta:
        settings = get_settings()
        if not settings.lyria_api_key:
            return await MockMusicProvider().generate(
                project_id=project_id, lyrics=lyrics, genre=genre, mood=mood, duration=duration
            )
        # TODO: integrate Lyria 3 Pro REST API once available
        log.warning("Lyria live integration not implemented — fallback to mock")
        return await MockMusicProvider().generate(
            project_id=project_id, lyrics=lyrics, genre=genre, mood=mood, duration=duration
        )


def get_music_provider():
    settings = get_settings()
    if settings.music_provider == "live":
        return LyriaMusicProvider()
    return MockMusicProvider()
