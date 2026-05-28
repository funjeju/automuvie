from app.services.render.audio_analyzer import allocate_timeline


def test_allocate_equal_split():
    tl = allocate_timeline(120.0, ["verse_1", "chorus_1", "verse_2", "chorus_2"])
    assert len(tl) == 4
    assert tl[0][1] == 0.0
    assert tl[-1][2] == 120.0
    # 마지막 segment는 정확히 audio_duration에 끝나야 함 (audio sync)
    assert all(end > start for _, start, end in tl)


def test_allocate_single_section():
    tl = allocate_timeline(60.0, ["verse_1"])
    assert tl == [("verse_1", 0.0, 60.0)]
