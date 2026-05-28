from pathlib import Path
from ...models.domain import Lyrics
from ...core.config import get_settings
from ...core.logger import get_logger

log = get_logger("subtitle")


ASS_HEADER = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
ScaledBorderAndShadow: yes
WrapStyle: 2

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Karaoke,Pretendard,72,&H00FFFFFF,&H00B14CFF,&H80000000,&H00000000,1,0,0,0,100,100,0,0,1,3,2,2,80,80,200,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""


def _to_ass_ts(seconds: float) -> str:
    if seconds < 0:
        seconds = 0
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = seconds - (h * 3600 + m * 60)
    return f"{h:01d}:{m:02d}:{s:05.2f}"


def _karaoke_line(start: float, end: float, text: str) -> str:
    words = [w for w in text.strip().split(" ") if w]
    if not words:
        return ""
    duration_cs = int(max(end - start, 0.5) * 100)
    per = max(20, duration_cs // max(len(words), 1))
    payload = "".join(f"{{\\kf{per}}}{w} " for w in words).rstrip()
    return f"Dialogue: 0,{_to_ass_ts(start)},{_to_ass_ts(end)},Karaoke,,0,0,0,,{payload}"


def build_ass_from_lyrics_timeline(lyrics: Lyrics, timeline: list[tuple[str, float, float]]) -> str:
    """lyrics + (sectionId, start, end) timeline → ASS karaoke."""
    by_id = {s.sectionId: s for s in lyrics.sections}
    lines: list[str] = []
    for sid, start, end in timeline:
        section = by_id.get(sid)
        if not section:
            continue
        lines.append(_karaoke_line(start, end, section.text))
    return ASS_HEADER + "\n".join(lines) + "\n"


class MockSubtitleProvider:
    """audio analysis 후 worker가 timeline을 채워주면 ASS 만들어 반환."""

    async def generate(self, *, project_id: str, audio_local_path: str, lyrics: Lyrics) -> str:
        # timeline은 worker에서 별도로 계산해 build_ass_from_lyrics_timeline로 호출하는 것이 정공법이지만
        # provider interface 호환성을 위해 균등 분할 fallback을 제공한다.
        try:
            from pydub import AudioSegment
            seg = AudioSegment.from_file(audio_local_path)
            total = len(seg) / 1000.0
        except Exception as e:
            log.warning(f"pydub fail, fallback duration=120s: {e}")
            total = 120.0
        n = max(len(lyrics.sections), 1)
        per = total / n
        timeline = [(s.sectionId, i * per, (i + 1) * per) for i, s in enumerate(lyrics.sections)]
        return build_ass_from_lyrics_timeline(lyrics, timeline)


class WhisperSubtitleProvider:
    async def generate(self, *, project_id: str, audio_local_path: str, lyrics: Lyrics) -> str:
        settings = get_settings()
        if not settings.openai_api_key and not settings.whisper_api_key:
            return await MockSubtitleProvider().generate(
                project_id=project_id, audio_local_path=audio_local_path, lyrics=lyrics
            )
        try:
            from openai import OpenAI
        except Exception:
            return await MockSubtitleProvider().generate(
                project_id=project_id, audio_local_path=audio_local_path, lyrics=lyrics
            )
        client = OpenAI(api_key=settings.openai_api_key or settings.whisper_api_key)
        with open(audio_local_path, "rb") as f:
            res = client.audio.transcriptions.create(
                model="whisper-1",
                file=f,
                response_format="verbose_json",
                timestamp_granularities=["word"],
            )
        # 간이 alignment: lyric section을 word timeline에 균등 매핑한다.
        words = getattr(res, "words", []) or []
        if not words:
            return await MockSubtitleProvider().generate(
                project_id=project_id, audio_local_path=audio_local_path, lyrics=lyrics
            )
        total = words[-1]["end"]
        n = max(len(lyrics.sections), 1)
        per = total / n
        timeline = [(s.sectionId, i * per, (i + 1) * per) for i, s in enumerate(lyrics.sections)]
        return build_ass_from_lyrics_timeline(lyrics, timeline)


def get_subtitle_provider():
    settings = get_settings()
    if settings.subtitle_provider == "live":
        return WhisperSubtitleProvider()
    return MockSubtitleProvider()
