from app.services.render.clip_planner import plan_section_clips


def test_plan_clips_repeats_with_variation():
    avail = [("a.mp4", 5.0), ("b.mp4", 4.0)]
    plan = plan_section_clips("verse_1", avail, needed_duration=20.0)
    assert sum(p.out_duration for p in plan) >= 20.0
    variants = [p.motion_variant for p in plan]
    # 단순 loop가 아니라 variant cinematic repeat이 적용되는지
    assert len(set(variants)) > 1


def test_plan_clips_short_duration():
    avail = [("a.mp4", 8.0)]
    plan = plan_section_clips("chorus_1", avail, needed_duration=5.0)
    assert len(plan) == 1
    assert plan[0].out_duration <= 8.0


def test_plan_clips_empty():
    plan = plan_section_clips("verse_1", [], needed_duration=10.0)
    assert plan == []
