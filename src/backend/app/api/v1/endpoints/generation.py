"""
Manual stage triggers (retry / resume용 internal endpoint).
MVP에서는 /project/create 한 번이면 전체 pipeline이 실행되지만,
docs §4 spec에 맞춰 각 단계별 endpoint도 노출한다.
"""
from fastapi import APIRouter, Depends
from ....core.auth import get_current_uid
from ....core.constants import ProjectStatus
from ....dto.common import ok
from ....dto.project_dto import ProjectIdRequest
from ....services.project_service import restart_step

router = APIRouter()


@router.post("/lyrics/generate")
async def lyrics_generate(body: ProjectIdRequest, uid: str = Depends(get_current_uid)):
    project = await restart_step(project_id=body.projectId, uid=uid, from_step=ProjectStatus.GENERATING_LYRICS)
    return ok({"status": ProjectStatus.GENERATING_LYRICS.value})


@router.post("/music/generate")
async def music_generate(body: ProjectIdRequest, uid: str = Depends(get_current_uid)):
    project = await restart_step(project_id=body.projectId, uid=uid, from_step=ProjectStatus.GENERATING_MUSIC)
    return ok({"status": ProjectStatus.GENERATING_MUSIC.value})


@router.post("/image/generate")
async def image_generate(body: ProjectIdRequest, uid: str = Depends(get_current_uid)):
    project = await restart_step(project_id=body.projectId, uid=uid, from_step=ProjectStatus.GENERATING_IMAGES)
    return ok({"status": ProjectStatus.GENERATING_IMAGES.value})


@router.post("/video/generate")
async def video_generate(body: ProjectIdRequest, uid: str = Depends(get_current_uid)):
    project = await restart_step(project_id=body.projectId, uid=uid, from_step=ProjectStatus.GENERATING_VIDEO)
    return ok({"status": ProjectStatus.GENERATING_VIDEO.value})


@router.post("/render/start")
async def render_start(body: ProjectIdRequest, uid: str = Depends(get_current_uid)):
    project = await restart_step(project_id=body.projectId, uid=uid, from_step=ProjectStatus.RENDERING)
    return ok({"status": ProjectStatus.RENDERING.value})
