from dataclasses import dataclass
from ...models.domain import SectionClips


@dataclass
class PlannedClip:
    section_id: str
    source_local: str
    in_offset: float
    out_duration: float
    motion_variant: str  # for repeat strategies: original | reverse | zoom | crop


def plan_section_clips(
    section_id: str,
    available_clips: list[tuple[str, float]],
    needed_duration: float,
) -> list[PlannedClip]:
    """
    available_clips: list of (local_path, duration)
    cinematic repeat 규칙 적용: A → B → A_zoom → C → B_crop ...
    """
    if not available_clips:
        return []

    variants = ["original", "reverse", "zoom", "crop", "original"]
    out: list[PlannedClip] = []
    acc = 0.0
    idx = 0
    while acc < needed_duration:
        local, dur = available_clips[idx % len(available_clips)]
        variant = variants[idx % len(variants)]
        take = min(dur, needed_duration - acc)
        out.append(
            PlannedClip(
                section_id=section_id,
                source_local=local,
                in_offset=0.0,
                out_duration=max(take, 0.5),
                motion_variant=variant,
            )
        )
        acc += take
        idx += 1
        if idx > 64:  # safety
            break
    return out
