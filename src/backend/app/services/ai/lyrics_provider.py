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


# Multi-line stanzas for mock — 4 lines per section
_MOCK_STANZAS = [
    "city lights reflected in the rain\nI walk these empty streets once more\nthe memory of you still remains\nlike a song I cannot ignore",
    "stay with me tonight under neon glow\nthe world outside can wait till dawn\ntime moves slow when you're letting go\nbut I'll keep holding on",
    "memories drift like smoke in empty rooms\nI reach for something I can't hold\nwinter fades and then the springtime blooms\nbut you were never growing old",
    "hold me closer when the daylight breaks\nand shadows chase the morning sky\nI count the stars until the silence aches\nand all I do is wonder why",
    "echoes of you between the silent streets\nI hear your voice inside the wind\nas every heartbeat softly repeats\nI find my way back to begin",
    "promise me one more dance in the dark\nbefore the night dissolves to grey\nyou leave a flame inside my heart\neven when you're miles away",
    "tomorrow fades but tonight is enough\nwe write our story line by line\nthe road ahead may still be rough\nbut this moment here is mine",
]


class MockLyricsProvider:
    async def generate(self, *, genre: str, mood: str, prompt: str, duration: int, language: str = "ko", style: str = "") -> Lyrics:
        scaffold = _structure_for_duration(duration)
        sections: list[LyricSection] = []
        for idx, (kind, order) in enumerate(scaffold):
            sections.append(
                LyricSection(
                    sectionId=f"{kind.value}_{order}",
                    type=kind,
                    order=idx + 1,
                    text=_MOCK_STANZAS[idx % len(_MOCK_STANZAS)],
                )
            )
        return Lyrics(sections=sections)


class GeminiLyricsProvider:
    """Google Gemini based lyric generator."""

    async def generate(self, *, genre: str, mood: str, prompt: str, duration: int, language: str = "ko", style: str = "") -> Lyrics:
        try:
            import google.generativeai as genai
        except Exception:
            log.warning("google-generativeai SDK 미설치 — mock fallback")
            return await MockLyricsProvider().generate(genre=genre, mood=mood, prompt=prompt, duration=duration, language=language, style=style)

        settings = get_settings()
        if not settings.google_genai_api_key:
            log.warning("GOOGLE_GENERATIVE_AI_API_KEY 미설정 — mock fallback")
            return await MockLyricsProvider().generate(genre=genre, mood=mood, prompt=prompt, duration=duration, language=language, style=style)

        genai.configure(api_key=settings.google_genai_api_key)
        model = genai.GenerativeModel("gemini-2.0-flash")

        scaffold = _structure_for_duration(duration)
        structure_hint = ", ".join(f"{k.value}_{o}" for k, o in scaffold)

        lang_instruction = {
            "ko": "한국어로만 작성하세요. 자연스럽고 감성적인 한국어 가사여야 합니다.",
            "en": "Write only in English. The lyrics should be poetic and evocative.",
            "mixed": "한국어와 영어를 자연스럽게 혼합하세요. 후렴구는 영어, 버스는 한국어 위주로 작성하세요.",
        }.get(language, "한국어로만 작성하세요.")

        style_hint = f"\n스타일 레퍼런스: {style}" if style else ""

        user_prompt = (
            f"당신은 전문 뮤직비디오 가사 작가입니다.\n"
            f"장르: {genre}\n무드: {mood}\n총 길이: {duration}초\n"
            f"주제/컨셉: {prompt or '자유'}{style_hint}\n\n"
            f"{lang_instruction}\n\n"
            f"다음 순서로 섹션을 작성하세요: {structure_hint}\n"
            f"각 섹션은 반드시 4줄로 작성하세요 (bridge는 2-3줄 허용).\n"
            f"각 줄은 노래 가사로 부를 수 있는 자연스러운 리듬감이 있어야 합니다.\n"
            f"줄바꿈은 \\n으로 표현하세요.\n\n"
            f"반드시 아래 JSON 형식으로만 응답하세요. 마크다운, 설명, 추가 텍스트 없이 순수 JSON만:\n"
            f'{{"sections":[{{"sectionId":"verse_1","type":"verse","order":1,"text":"1번째 줄\\n2번째 줄\\n3번째 줄\\n4번째 줄"}}]}}'
        )

        try:
            response = model.generate_content(user_prompt)
            raw = response.text.strip()
            # Strip markdown code blocks if present
            if raw.startswith("```"):
                raw = raw.split("```")[1]
                if raw.startswith("json"):
                    raw = raw[4:]
            data = json.loads(raw[raw.index("{") : raw.rindex("}") + 1])
            return Lyrics.model_validate(data)
        except Exception as e:
            log.error(f"Gemini lyrics parse failed: {e}")
            return await MockLyricsProvider().generate(genre=genre, mood=mood, prompt=prompt, duration=duration, language=language, style=style)


def get_lyrics_provider():
    settings = get_settings()
    if settings.lyrics_provider == "live":
        return GeminiLyricsProvider()
    return MockLyricsProvider()
