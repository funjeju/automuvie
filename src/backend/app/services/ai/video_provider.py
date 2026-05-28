from pathlib import Path
from ...models.domain import Lyrics, SectionImages, SectionClips, VideoClip
from ...repositories.storage_repository import get_storage_repository
from ...core.constants import DEFAULT_RESOLUTION, DEFAULT_FPS
from ...core.config import get_settings
from ...core.logger import get_logger

log = get_logger("video")


def _ken_burns_clip(image_local: str, out_local: str, duration: float, mode: str) -> None:
    """ffmpeg-python으로 Ken Burns 스타일 motion clip 생성. fallback strategy로도 동일하게 사용."""
    import ffmpeg

    w, h = DEFAULT_RESOLUTION
    frames = int(duration * DEFAULT_FPS)
    if mode == "zoom_in":
        zoom_expr = f"zoom+0.0006*on"
        x_expr = "iw/2-(iw/zoom/2)"
        y_expr = "ih/2-(ih/zoom/2)"
    elif mode == "zoom_out":
        zoom_expr = f"max(1.0, 1.25-0.0006*on)"
        x_expr = "iw/2-(iw/zoom/2)"
        y_expr = "ih/2-(ih/zoom/2)"
    elif mode == "pan_left":
        zoom_expr = "1.2"
        x_expr = "(iw-iw/zoom)*on/{}".format(frames)
        y_expr = "ih/2-(ih/zoom/2)"
    else:  # pan_right
        zoom_expr = "1.2"
        x_expr = "(iw-iw/zoom)*(1-on/{})".format(frames)
        y_expr = "ih/2-(ih/zoom/2)"

    (
        ffmpeg.input(image_local, loop=1, t=duration)
        .filter(
            "zoompan",
            z=zoom_expr,
            x=x_expr,
            y=y_expr,
            d=frames,
            s=f"{w}x{h}",
            fps=DEFAULT_FPS,
        )
        .filter("format", "yuv420p")
        .output(out_local, vcodec="libx264", pix_fmt="yuv420p", r=DEFAULT_FPS, preset="medium", t=duration)
        .overwrite_output()
        .run(quiet=True)
    )


class MockVideoProvider:
    """Ken Burns motion으로 image → mp4 clip 생성. fallback strategy와 동일."""

    MOTIONS = ["zoom_in", "zoom_out", "pan_left", "pan_right"]

    async def generate(
        self,
        *,
        project_id: str,
        lyrics: Lyrics,
        images: list[SectionImages],
        genre: str,
        mood: str,
    ) -> list[SectionClips]:
        storage = get_storage_repository()
        out: list[SectionClips] = []
        for section_imgs in images:
            clips: list[VideoClip] = []
            for idx, image_url in enumerate(section_imgs.images[:3]):
                local_in = image_url.replace("local:", "") if image_url.startswith("local:") else storage.local_path(
                    project_id, "images", f"{section_imgs.sectionId}_{idx+1}.png"
                )
                out_name = f"{section_imgs.sectionId}_{idx+1}.mp4"
                local_out = storage.local_path(project_id, "clips", out_name)
                Path(local_out).parent.mkdir(parents=True, exist_ok=True)
                duration = 8.0 + (idx * 0.5)
                motion = self.MOTIONS[idx % len(self.MOTIONS)]
                try:
                    _ken_burns_clip(local_in, local_out, duration, motion)
                except Exception as e:
                    log.error(f"ken-burns fail {section_imgs.sectionId}/{idx}: {e}")
                    continue
                url = storage.upload(project_id, "clips", out_name, local_out)
                clips.append(VideoClip(url=url, duration=duration))
            out.append(SectionClips(sectionId=section_imgs.sectionId, clips=clips))
        return out


class VeoVideoProvider:
    async def generate(
        self,
        *,
        project_id: str,
        lyrics: Lyrics,
        images: list[SectionImages],
        genre: str,
        mood: str,
    ) -> list[SectionClips]:
        settings = get_settings()
        if not settings.veo_api_key:
            return await MockVideoProvider().generate(
                project_id=project_id, lyrics=lyrics, images=images, genre=genre, mood=mood
            )
        log.warning("Veo live integration placeholder — fallback to ken-burns")
        return await MockVideoProvider().generate(
            project_id=project_id, lyrics=lyrics, images=images, genre=genre, mood=mood
        )


def get_video_provider():
    settings = get_settings()
    if settings.video_provider == "live":
        return VeoVideoProvider()
    return MockVideoProvider()
