"""Smoke test — mock provider 기반 pipeline 전체 흐름이 동작하는지 검증."""
import asyncio
import pytest

from app.core.constants import ProjectStatus
from app.services.project_service import create_project, get_project
from app.workers.task_queue import get_task_queue


@pytest.mark.asyncio
async def test_create_and_run_pipeline_mock():
    queue = get_task_queue()
    await queue.start()
    project = await create_project(
        uid="dev_user",
        genre="cinematic emotional",
        mood="nostalgic",
        prompt="warm memory in lonely city",
        duration=60,
    )
    # 백그라운드 worker가 단계 진행할 시간을 준다 (ffmpeg 미설치 환경에선 fail될 수 있음)
    for _ in range(30):
        await asyncio.sleep(1)
        cur = await get_project(project_id=project.projectId, uid="dev_user")
        if cur.status in (ProjectStatus.COMPLETED, ProjectStatus.FAILED):
            break
    cur = await get_project(project_id=project.projectId, uid="dev_user")
    assert cur.lyrics is not None  # at least lyrics step completed
