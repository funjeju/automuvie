from app.core.constants import SectionType
from app.models.domain import Lyrics, LyricSection
from app.services.ai.subtitle_provider import build_ass_from_lyrics_timeline


def _lyrics():
    return Lyrics(sections=[
        LyricSection(sectionId="verse_1", type=SectionType.VERSE, order=1, text="city lights"),
        LyricSection(sectionId="chorus_1", type=SectionType.CHORUS, order=2, text="stay with me"),
    ])


def test_ass_header_and_dialogue_lines():
    timeline = [("verse_1", 0.0, 10.0), ("chorus_1", 10.0, 20.0)]
    ass = build_ass_from_lyrics_timeline(_lyrics(), timeline)
    assert "[Script Info]" in ass
    assert "Style: Karaoke" in ass
    assert ass.count("Dialogue:") == 2
    assert "\\kf" in ass  # karaoke fill effect mandatory


def test_ass_skips_unknown_section():
    timeline = [("missing", 0.0, 10.0), ("verse_1", 10.0, 20.0)]
    ass = build_ass_from_lyrics_timeline(_lyrics(), timeline)
    assert ass.count("Dialogue:") == 1
