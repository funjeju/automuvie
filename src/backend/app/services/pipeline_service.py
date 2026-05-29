"""
Pipeline orchestrator — core.md §7 순서를 강제한다.
Resume 규칙: 성공한 단계는 재생성 금지 (project document 기준).
Retry 규칙: 단계당 max 3회, exponential backoff.
Cache 규칙: lyrics/music/image/video는 (genre+mood+prompt+duration+seed) 기준 cache hit 시 재사용.
"""

from __future__ import annotations
import asyncio
import json
import uuid
from pathlib import Path
from ..core.constants import (
    ProjectStatus,
    MAX_RETRY_COUNT,
    AssetType,
    DEFAULT_RESOLUTION,
)
from ..core.logger import get_logger
from ..core.errors import PipelineError
from ..models.domain import (
    Project,
    TimelineSegment,
    Lyrics,
    AudioMeta,
    SectionImages,
    SectionClips,
)
from ..repositories.project_repository import get_project_repository
from ..repositories.storage_repository import get_storage_repository
from ..repositories.render_repository import get_render_repository
from ..repositories.asset_repository import get_asset_repository, AssetMeta
from ..repositories.cache_repository import get_cache, make_cache_key
from ..models.domain import RenderJob
from .ai.lyrics_provider import get_lyrics_provider
from .ai.music_provider import get_music_provider
from .ai.image_provider import get_image_provider
from .ai.video_provider import get_video_provider
from .ai.subtitle_provider import get_subtitle_provider, build_ass_from_lyrics_timeline
from .render.audio_analyzer import measure_audio_duration, allocate_timeline
from .render.clip_planner import plan_section_clips
from .render.render_engine import RenderInputs, render

log = get_logger("pipeline")


async def _with_retry(label: str, coro_factory, max_retry: int = MAX_RETRY_COUNT):
    last_err: Exception | None = None
    for attempt in range(1, max_retry + 1):
        try:
            return await coro_factory()
        except Exception as e:
            last_err = e
            log.warning(f"[{label}] attempt {attempt}/{max_retry} failed: {e}")
            await asyncio.sleep(min(2 ** attempt, 8))
    raise PipelineError(message=f"{label} 단계가 {max_retry}회 실패했습니다.") from last_err


def _resolve_audio_local(project: Project) -> str:
    """audio.wav가 없으면 audio.mp3 fallback (live provider 호환)."""
    storage = get_storage_repository()
    wav = Path(storage.local_path(project.projectId, "audio", "audio.wav"))
    if wav.exists():
        return str(wav)
    mp3 = Path(storage.local_path(project.projectId, "audio", "audio.mp3"))
    return str(mp3)


def _clip_local_path(project_id: str, filename: str) -> str:
    return get_storage_repository().local_path(project_id, "clips", filename)


def _cache_key(stage: str, project: Project) -> str:
    return make_cache_key(
        stage,
        genre=project.genre,
        mood=project.mood,
        prompt=project.prompt or "",
        duration=project.duration,
        seed=None,
    )


async def _record_asset(*, project: Project, asset_type: AssetType, section_id: str | None, url: str, **extra) -> None:
    repo = get_asset_repository()
    await repo.save(
        AssetMeta(
            assetId=f"asset_{uuid.uuid4().hex[:16]}",
            projectId=project.projectId,
            uid=project.uid,
            assetType=asset_type,
            sectionId=section_id,
            url=url,
            **extra,
        )
    )


async def run_pipeline(project_id: str) -> None:
    repo = get_project_repository()
    storage = get_storage_repository()
    render_repo = get_render_repository()
    cache = get_cache()
    project = await repo.get(project_id)
    if not project:
        log.error(f"project not found: {project_id}")
        return

    try:
        # 1. Lyrics
        if not project.lyrics:
            await repo.set_status(project_id, ProjectStatus.GENERATING_LYRICS)
            key = _cache_key("lyrics", project)
            cached = cache.get(key)
            if cached:
                log.info(f"[cache hit] lyrics {key}")
                lyrics = Lyrics.model_validate(cached)
            else:
                provider = get_lyrics_provider()
                lyrics = await _with_retry(
                    "lyrics",
                    lambda: provider.generate(
                        genre=project.genre, mood=project.mood, prompt=project.prompt, duration=project.duration,
                        language=getattr(project, "language", "ko"), style=getattr(project, "style", ""),
                    ),
                )
                cache.set(key, lyrics.model_dump(mode="json"))
            project.lyrics = lyrics
            url = storage.write_text(
                project_id, "lyrics", "lyrics.json", json.dumps(lyrics.model_dump(mode="json"), ensure_ascii=False, indent=2)
            )
            await _record_asset(project=project, asset_type=AssetType.LYRICS, section_id=None, url=url)
            await repo.update(project)

        # 2. Music
        if not project.audio:
            await repo.set_status(project_id, ProjectStatus.GENERATING_MUSIC)
            provider = get_music_provider()
            audio = await _with_retry(
                "music",
                lambda: provider.generate(
                    project_id=project_id,
                    lyrics=project.lyrics,  # type: ignore[arg-type]
                    genre=project.genre,
                    mood=project.mood,
                    duration=project.duration,
                ),
            )
            project.audio = audio
            await _record_asset(
                project=project,
                asset_type=AssetType.AUDIO,
                section_id=None,
                url=audio.audioUrl,
                duration=audio.duration,
            )
            await repo.update(project)

        # 3. Images
        if not project.images:
            await repo.set_status(project_id, ProjectStatus.GENERATING_IMAGES)
            provider = get_image_provider()
            images = await _with_retry(
                "images",
                lambda: provider.generate(
                    project_id=project_id,
                    lyrics=project.lyrics,  # type: ignore[arg-type]
                    genre=project.genre,
                    mood=project.mood,
                ),
            )
            project.images = images
            w, h = DEFAULT_RESOLUTION
            for section_imgs in images:
                for url in section_imgs.images:
                    await _record_asset(
                        project=project,
                        asset_type=AssetType.IMAGE,
                        section_id=section_imgs.sectionId,
                        url=url,
                        width=w,
                        height=h,
                    )
            await repo.update(project)

        # 4. Video clips
        if not project.clips:
            await repo.set_status(project_id, ProjectStatus.GENERATING_VIDEO)
            provider = get_video_provider()
            clips = await _with_retry(
                "video",
                lambda: provider.generate(
                    project_id=project_id,
                    lyrics=project.lyrics,  # type: ignore[arg-type]
                    images=project.images,
                    genre=project.genre,
                    mood=project.mood,
                ),
            )
            project.clips = clips
            for section_clips in clips:
                for clip in section_clips.clips:
                    await _record_asset(
                        project=project,
                        asset_type=AssetType.VIDEO,
                        section_id=section_clips.sectionId,
                        url=clip.url,
                        duration=clip.duration,
                    )
            await repo.update(project)

        # 5. Audio analysis + timeline
        await repo.set_status(project_id, ProjectStatus.GENERATING_SUBTITLE)
        audio_local = _resolve_audio_local(project)
        audio_duration = measure_audio_duration(audio_local)
        if audio_duration <= 0:
            audio_duration = float(project.duration)
        section_ids = [s.sectionId for s in project.lyrics.sections]  # type: ignore[union-attr]
        tl = allocate_timeline(audio_duration, section_ids)
        project.timeline = [TimelineSegment(sectionId=sid, start=s, end=e) for sid, s, e in tl]
        await repo.update(project)

        # 6. Subtitle — word-level alignment 시도 후 timeline과 동기화한 ASS 재생성
        provider = get_subtitle_provider()
        await _with_retry(
            "subtitle",
            lambda: provider.generate(project_id=project_id, audio_local_path=audio_local, lyrics=project.lyrics),  # type: ignore[arg-type]
        )
        ass_text = build_ass_from_lyrics_timeline(
            project.lyrics, [(s.sectionId, s.start, s.end) for s in project.timeline]  # type: ignore[arg-type]
        )
        subtitle_url = storage.write_text(project_id, "subtitle", "subtitle.ass", ass_text)
        project.subtitleUrl = subtitle_url
        await _record_asset(project=project, asset_type=AssetType.SUBTITLE, section_id=None, url=subtitle_url)
        await repo.update(project)

        # 7. Render — Renders collection에 lifecycle을 기록한다.
        render_id = f"render_{uuid.uuid4().hex[:12]}"
        await render_repo.create(RenderJob(renderId=render_id, projectId=project_id, uid=project.uid, status="rendering"))
        await repo.set_status(project_id, ProjectStatus.RENDERING)

        planned = []
        clips_by_section = {c.sectionId: c.clips for c in project.clips}
        for seg in project.timeline:
            avail = clips_by_section.get(seg.sectionId, [])
            avail_paths: list[tuple[str, float]] = []
            for idx, c in enumerate(avail):
                local = _clip_local_path(project_id, f"{seg.sectionId}_{idx+1}.mp4")
                avail_paths.append((local, c.duration))
            planned.extend(plan_section_clips(seg.sectionId, avail_paths, needed_duration=seg.end - seg.start))

        out_dir = Path(storage.local_path(project_id, "render", "_")).parent

        loop = asyncio.get_event_loop()

        def _on_progress(step: str, pct: int) -> None:
            # async repo update를 sync 컨텍스트(ffmpeg)에서 안전하게 트리거
            asyncio.run_coroutine_threadsafe(render_repo.update_step(render_id, step, pct), loop)
            log.info(f"render step={step} pct={pct}")

        outputs = await asyncio.to_thread(
            render,
            RenderInputs(
                project_id=project_id,
                audio_local=audio_local,
                subtitle_local=storage.local_path(project_id, "subtitle", "subtitle.ass"),
                planned=planned,
                target_duration=audio_duration,
                out_dir=out_dir,
            ),
            _on_progress,
        )

        final_url = storage.upload(project_id, "render", "final.mp4", outputs["final"])
        preview_url = storage.upload(project_id, "render", "preview.mp4", outputs["preview"])
        project.finalVideoUrl = final_url
        project.previewUrl = preview_url
        await _record_asset(project=project, asset_type=AssetType.FINAL, section_id=None, url=final_url)
        await _record_asset(project=project, asset_type=AssetType.PREVIEW, section_id=None, url=preview_url)

        # docs/6 — metadata.json 출력 contract
        from ..core.constants import DEFAULT_FPS, DEFAULT_RESOLUTION as RES
        metadata = {
            "projectId": project_id,
            "duration": audio_duration,
            "resolution": f"{RES[0]}x{RES[1]}",
            "fps": DEFAULT_FPS,
            "finalUrl": final_url,
            "previewUrl": preview_url,
            "subtitleUrl": subtitle_url,
            "audioUrl": project.audio.audioUrl if project.audio else None,
        }
        storage.write_text(
            project_id, "render", "metadata.json", json.dumps(metadata, ensure_ascii=False, indent=2)
        )

        await render_repo.mark_completed(render_id)
        await repo.set_status(project_id, ProjectStatus.COMPLETED)
        await repo.update(project)
        log.info(f"pipeline completed: {project_id}")

    except Exception as e:
        log.exception(f"pipeline failed: {e}")
        project.retryCount += 1
        await repo.update(project)
        await repo.set_status(
            project_id,
            ProjectStatus.FAILED,
            error_code="PIPELINE_FAILED",
            error_message="생성 파이프라인 처리 중 문제가 발생했습니다. 다시 시도해주세요.",
        )
        try:
            # render job이 시작된 상태라면 failed로 마킹
            if "render_id" in locals():
                await render_repo.mark_failed(locals()["render_id"])
        except Exception:
            pass
