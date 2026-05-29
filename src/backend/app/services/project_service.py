from __future__ import annotations
import uuid
from ..core.constants import ProjectStatus
from ..core.errors import NotFoundError, ForbiddenError
from ..models.domain import Project
from ..repositories.project_repository import get_project_repository
from ..workers.task_queue import get_task_queue
from .pipeline_service import run_pipeline


async def create_project(*, uid: str, genre: str, mood: str, prompt: str, duration: int, language: str = "ko", style: str = "") -> Project:
    repo = get_project_repository()
    project = Project(
        projectId=f"proj_{uuid.uuid4().hex[:12]}",
        uid=uid,
        genre=genre,
        mood=mood,
        prompt=prompt or "",
        duration=duration,
        language=language,
        style=style,
        status=ProjectStatus.QUEUED,
    )
    await repo.create(project)

    queue = get_task_queue()
    await queue.submit(lambda: run_pipeline(project.projectId))
    return project


async def get_project(*, project_id: str, uid: str) -> Project:
    repo = get_project_repository()
    project = await repo.get(project_id)
    if not project:
        raise NotFoundError()
    if project.uid != uid:
        raise ForbiddenError()
    return project


async def cancel_project(*, project_id: str, uid: str) -> Project:
    repo = get_project_repository()
    project = await repo.get(project_id)
    if not project:
        raise NotFoundError()
    if project.uid != uid:
        raise ForbiddenError()
    if project.status in (ProjectStatus.COMPLETED, ProjectStatus.FAILED, ProjectStatus.CANCELLED):
        return project
    await repo.set_status(project_id, ProjectStatus.CANCELLED)
    project.status = ProjectStatus.CANCELLED
    return project


async def restart_step(*, project_id: str, uid: str, from_step: ProjectStatus) -> Project:
    """resume helper. 성공한 단계는 그대로 두고, from_step에 해당하는 asset만 비운다."""
    repo = get_project_repository()
    project = await repo.get(project_id)
    if not project:
        raise NotFoundError()
    if project.uid != uid:
        raise ForbiddenError()

    reset_map = {
        ProjectStatus.GENERATING_LYRICS: ["lyrics", "audio", "images", "clips", "subtitleUrl", "previewUrl", "finalVideoUrl"],
        ProjectStatus.GENERATING_MUSIC: ["audio", "subtitleUrl", "previewUrl", "finalVideoUrl"],
        ProjectStatus.GENERATING_IMAGES: ["images", "clips", "subtitleUrl", "previewUrl", "finalVideoUrl"],
        ProjectStatus.GENERATING_VIDEO: ["clips", "previewUrl", "finalVideoUrl"],
        ProjectStatus.GENERATING_SUBTITLE: ["subtitleUrl", "previewUrl", "finalVideoUrl"],
        ProjectStatus.RENDERING: ["previewUrl", "finalVideoUrl"],
    }
    for field in reset_map.get(from_step, []):
        if field in {"lyrics", "audio", "subtitleUrl", "previewUrl", "finalVideoUrl"}:
            setattr(project, field, None)
        else:
            setattr(project, field, [])

    project.errorCode = None
    project.errorMessage = None
    project.status = ProjectStatus.QUEUED
    await repo.update(project)

    queue = get_task_queue()
    await queue.submit(lambda: run_pipeline(project.projectId))
    return project
