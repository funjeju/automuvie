from fastapi import APIRouter, Depends
from ....core.auth import get_current_uid
from ....core.constants import STATUS_PROGRESS_MAP, ProjectStatus
from ....dto.common import ok
from ....services.project_service import get_project

router = APIRouter()


@router.get("/render/status/{project_id}")
async def render_status(project_id: str, uid: str = Depends(get_current_uid)):
    project = await get_project(project_id=project_id, uid=uid)
    current_step = {
        ProjectStatus.GENERATING_LYRICS: "lyrics_generation",
        ProjectStatus.GENERATING_MUSIC: "music_generation",
        ProjectStatus.GENERATING_IMAGES: "image_generation",
        ProjectStatus.GENERATING_VIDEO: "video_generation",
        ProjectStatus.GENERATING_SUBTITLE: "subtitle_generation",
        ProjectStatus.RENDERING: "rendering",
        ProjectStatus.COMPLETED: "completed",
        ProjectStatus.QUEUED: "queued",
        ProjectStatus.FAILED: "failed",
        ProjectStatus.CANCELLED: "cancelled",
    }.get(project.status, "queued")

    return ok({
        "projectId": project.projectId,
        "status": project.status.value,
        "progress": project.progress or STATUS_PROGRESS_MAP.get(project.status, 0),
        "currentStep": current_step,
        "errorCode": project.errorCode,
        "errorMessage": project.errorMessage,
    })
