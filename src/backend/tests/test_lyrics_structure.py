import pytest
from app.services.ai.lyrics_provider import MockLyricsProvider


@pytest.mark.asyncio
async def test_60s_structure_has_verse_chorus():
    p = MockLyricsProvider()
    lyrics = await p.generate(genre="cinematic", mood="nostalgic", prompt="", duration=60)
    types = [s.type.value for s in lyrics.sections]
    assert "verse" in types
    assert "chorus" in types


@pytest.mark.asyncio
async def test_120s_structure_has_bridge():
    p = MockLyricsProvider()
    lyrics = await p.generate(genre="cinematic", mood="nostalgic", prompt="", duration=120)
    types = [s.type.value for s in lyrics.sections]
    assert "bridge" in types


@pytest.mark.asyncio
async def test_180s_has_three_verses():
    p = MockLyricsProvider()
    lyrics = await p.generate(genre="cinematic", mood="nostalgic", prompt="", duration=180)
    verses = [s for s in lyrics.sections if s.type.value == "verse"]
    assert len(verses) >= 3
