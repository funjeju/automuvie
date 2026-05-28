import json
from ...models.domain import Lyrics, LyricSection
from ...core.constants import SectionType
from ...core.config import get_settings
from ...core.logger import get_logger

log = get_logger("lyrics")


def _structure_for_duration(duration: int) -> list[tuple[SectionType, int]]:
    if duration <= 75:
        return [(SectionType.VERSE, 1), (SectionType.CHORUS, 1), (SectionType.VERSE, 2), (SectionType.CHORUS, 2)]
    if duration <= 130:
        return [
            (SectionType.VERSE, 1),
            (SectionType.CHORUS, 1),
            (SectionType.VERSE, 2),
            (SectionType.CHORUS, 2),
            (SectionType.BRIDGE, 1),
            (SectionType.CHORUS, 3),
        ]
    return [
        (SectionType.VERSE, 1),
        (SectionType.CHORUS, 1),
        (SectionType.VERSE, 2),
        (SectionType.CHORUS, 2),
        (SectionType.BRIDGE, 1),
        (SectionType.VERSE, 3),
        (SectionType.CHORUS, 3),
    ]


class MockLyricsProvider:
    async def generate(self, *, genre: str, mood: str, prompt: str, duration: int) -> Lyrics:
        scaffold = _structure_for_duration(duration)
        sections: list[LyricSection] = []
        themes = [
            "city lights falling softly through the rain",
            "stay with me tonight under neon glow",
            "memories drift like smoke in empty rooms",
            "hold me closer when the daylight breaks",
            "echoes of you between the silent streets",
            "promise me one more dance in the dark",
            "tomorrow fades but tonight is enough",
        ]
        for idx, (kind, order) in enumerate(scaffold):
            sections.append(
                LyricSection(
                    sectionId=f"{kind.value}_{order}",
                    type=kind,
                    order=idx + 1,
                    text=themes[idx % len(themes)],
                )
            )
        return Lyrics(sections=sections)


class ClaudeLyricsProvider:
    """Anthropic Claude based lyric generator."""

    async def generate(self, *, genre: str, mood: str, prompt: str, duration: int) -> Lyrics:
        try:
            from anthropic import Anthropic
        except Exception:
            log.warning("anthropic SDK 미설치 — mock fallback")
            return await MockLyricsProvider().generate(genre=genre, mood=mood, prompt=prompt, duration=duration)

        settings = get_settings()
        if not settings.claude_api_key:
            return await MockLyricsProvider().generate(genre=genre, mood=mood, prompt=prompt, duration=duration)

        client = Anthropic(api_key=settings.claude_api_key)
        scaffold = _structure_for_duration(duration)
        structure_hint = ", ".join(f"{k.value}_{o}" for k, o in scaffold)

        user_prompt = (
            f"You are a cinematic music lyric writer.\n"
            f"Genre: {genre}\nMood: {mood}\nDuration: {duration}s\nUser prompt: {prompt or '(none)'}\n"
            f"Generate lyrics with these sections in order: {structure_hint}.\n"
            f"Return ONLY JSON with shape: "
            f'{{"sections":[{{"sectionId":"verse_1","type":"verse","order":1,"text":"..."}}]}}'
        )

        msg = client.messages.create(
            model="claude-opus-4-7",
            max_tokens=2048,
            messages=[{"role": "user", "content": user_prompt}],
        )
        raw = "".join(block.text for block in msg.content if hasattr(block, "text")).strip()
        try:
            data = json.loads(raw[raw.index("{") : raw.rindex("}") + 1])
            return Lyrics.model_validate(data)
        except Exception as e:
            log.error(f"Claude lyrics parse failed: {e}")
            return await MockLyricsProvider().generate(genre=genre, mood=mood, prompt=prompt, duration=duration)


def get_lyrics_provider():
    settings = get_settings()
    if settings.lyrics_provider == "live":
        return ClaudeLyricsProvider()
    return MockLyricsProvider()
