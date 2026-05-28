from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable
from ...core.constants import DEFAULT_RESOLUTION, PREVIEW_RESOLUTION, DEFAULT_FPS, VIDEO_BITRATE, AUDIO_BITRATE
from ...core.logger import get_logger
from ...core.errors import RenderError
from .clip_planner import PlannedClip

log = get_logger("render_engine")


@dataclass
class RenderInputs:
    project_id: str
    audio_local: str
    subtitle_local: str
    planned: list[PlannedClip]
    target_duration: float
    out_dir: Path


def _ensure_ffmpeg():
    try:
        import ffmpeg  # noqa
    except Exception as e:
        raise RenderError(message=f"ffmpeg-python 미설치: {e}")


def _normalize_clip(src: str, dst: str, duration: float, variant: str, w: int, h: int) -> None:
    """clip을 target resolution/fps/duration으로 정규화하면서 variant motion 적용."""
    import ffmpeg

    stream = ffmpeg.input(src)
    v = stream.video
    a = stream.audio if False else None  # 영상 clip의 오디오는 사용 안함 (audio는 최종에서 1개만 mux)

    if variant == "reverse":
        v = v.filter("reverse")
    elif variant == "zoom":
        v = v.filter("scale", w * 1.15, h * 1.15).filter("crop", w, h)
    elif variant == "crop":
        v = v.filter("crop", "in_w*0.85", "in_h*0.85").filter("scale", w, h)

    v = v.filter("scale", w, h, force_original_aspect_ratio="increase").filter("crop", w, h)
    v = v.filter("setsar", "1")
    v = v.filter("fps", DEFAULT_FPS)
    (
        ffmpeg.output(v, dst, t=duration, vcodec="libx264", pix_fmt="yuv420p", an=None, preset="medium", r=DEFAULT_FPS)
        .overwrite_output()
        .run(quiet=True)
    )


def _concat_with_crossfade(parts: list[str], out_path: str, w: int, h: int, fade_dur: float = 0.6) -> None:
    """xfade 기반 cross dissolve 연결. ffmpeg-python graph 사용."""
    import ffmpeg

    if not parts:
        raise RenderError(message="합성할 clip이 없습니다.")
    if len(parts) == 1:
        # 그대로 복사
        ffmpeg.input(parts[0]).output(out_path, vcodec="copy", an=None).overwrite_output().run(quiet=True)
        return

    # 각 입력의 duration probe
    durations: list[float] = []
    for p in parts:
        meta = ffmpeg.probe(p)
        durations.append(float(meta["format"]["duration"]))

    inputs = [ffmpeg.input(p) for p in parts]
    chain = inputs[0].video
    offset = durations[0] - fade_dur
    for i in range(1, len(inputs)):
        chain = ffmpeg.filter(
            [chain, inputs[i].video],
            "xfade",
            transition="fade",
            duration=fade_dur,
            offset=offset,
        )
        offset += durations[i] - fade_dur

    (
        ffmpeg.output(chain, out_path, vcodec="libx264", pix_fmt="yuv420p", preset="medium", r=DEFAULT_FPS, an=None)
        .overwrite_output()
        .run(quiet=True)
    )


def _mux_audio_subtitle(video_path: str, audio_path: str, subtitle_path: str, out_path: str, audio_duration: float) -> None:
    import ffmpeg

    video = ffmpeg.input(video_path)
    audio = ffmpeg.input(audio_path)

    # subtitles 필터는 ffmpeg에서 경로 escape가 까다로움 → forward slash 사용
    sub_path_filter = subtitle_path.replace("\\", "/").replace(":", "\\:")
    v = video.video.filter("subtitles", sub_path_filter)
    v = v.filter("fade", type="in", start_time=0, duration=0.8)
    v = v.filter("fade", type="out", start_time=max(audio_duration - 0.8, 0), duration=0.8)

    (
        ffmpeg.output(
            v,
            audio.audio,
            out_path,
            vcodec="libx264",
            acodec="aac",
            pix_fmt="yuv420p",
            preset="medium",
            r=DEFAULT_FPS,
            video_bitrate=VIDEO_BITRATE,
            audio_bitrate=AUDIO_BITRATE,
            shortest=None,
            t=audio_duration,
        )
        .overwrite_output()
        .run(quiet=True)
    )


def _downscale(src: str, dst: str, target_w: int, target_h: int) -> None:
    import ffmpeg
    (
        ffmpeg.input(src)
        .filter("scale", target_w, target_h)
        .output(dst, vcodec="libx264", acodec="aac", pix_fmt="yuv420p", preset="medium", r=DEFAULT_FPS, video_bitrate="4M")
        .overwrite_output()
        .run(quiet=True)
    )


def render(inputs: RenderInputs, on_progress: callable | None = None) -> dict[str, str]:
    _ensure_ffmpeg()
    w, h = DEFAULT_RESOLUTION
    inputs.out_dir.mkdir(parents=True, exist_ok=True)

    if on_progress:
        on_progress("timeline_analysis", 5)

    # 1) 모든 planned clip을 단일 spec(WxH/fps/duration)로 정규화
    normalized: list[str] = []
    for i, p in enumerate(inputs.planned):
        norm_path = inputs.out_dir / f"norm_{i:03d}.mp4"
        _normalize_clip(p.source_local, str(norm_path), p.out_duration, p.motion_variant, w, h)
        normalized.append(str(norm_path))

    if on_progress:
        on_progress("clip_selection", 35)

    # 2) cross dissolve concat
    concat_path = inputs.out_dir / "concat.mp4"
    _concat_with_crossfade(normalized, str(concat_path), w, h)

    if on_progress:
        on_progress("transition", 60)
        on_progress("subtitle_burn", 75)

    # 3) audio + subtitle mux (subtitle burn-in)
    final_path = inputs.out_dir / "final.mp4"
    _mux_audio_subtitle(str(concat_path), inputs.audio_local, inputs.subtitle_local, str(final_path), inputs.target_duration)

    if on_progress:
        on_progress("audio_sync", 90)

    # 4) preview downscale
    preview_path = inputs.out_dir / "preview.mp4"
    pw, ph = PREVIEW_RESOLUTION
    _downscale(str(final_path), str(preview_path), pw, ph)

    if on_progress:
        on_progress("export", 100)

    # cleanup intermediate
    for n in normalized:
        try:
            Path(n).unlink(missing_ok=True)
        except Exception:
            pass
    try:
        concat_path.unlink(missing_ok=True)
    except Exception:
        pass

    return {
        "final": str(final_path),
        "preview": str(preview_path),
    }
