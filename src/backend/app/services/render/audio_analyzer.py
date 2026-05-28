from ...core.logger import get_logger

log = get_logger("audio_analyzer")


def measure_audio_duration(local_path: str) -> float:
    try:
        from pydub import AudioSegment
        seg = AudioSegment.from_file(local_path)
        return len(seg) / 1000.0
    except Exception as e:
        log.warning(f"pydub fail ({e}) — fallback ffprobe via ffmpeg")
        try:
            import ffmpeg
            meta = ffmpeg.probe(local_path)
            return float(meta["format"]["duration"])
        except Exception as e2:
            log.error(f"ffprobe fail: {e2}")
            return 0.0


def allocate_timeline(audio_duration: float, section_ids: list[str]) -> list[tuple[str, float, float]]:
    """audio duration 기준 section을 균등 배치한다. (source of truth = audio)"""
    n = max(len(section_ids), 1)
    per = audio_duration / n
    out: list[tuple[str, float, float]] = []
    for idx, sid in enumerate(section_ids):
        start = idx * per
        end = (idx + 1) * per if idx < n - 1 else audio_duration
        out.append((sid, start, end))
    return out
