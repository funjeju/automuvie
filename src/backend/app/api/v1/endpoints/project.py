from fastapi import APIRouter, Depends
from ....core.auth import get_current_uid
from ....core.constants import STATUS_PROGRESS_MAP, ProjectStatus
from ....dto.common import ok
from ....dto.project_dto import (
    CreateProjectRequest,
    ProjectIdRequest,
)
from ....repositories.project_repository import get_project_repository
from ....repositories.asset_repository import get_asset_repository
from ....services.project_service import cancel_project, create_project, get_project, restart_step

router = APIRouter()


@router.get("/projects")
async def list_projects(uid: str = Depends(get_current_uid), limit: int = 50):
    repo = get_project_repository()
    projects = await repo.list_by_uid(uid, limit=limit)
    return ok(
        {
            "items": [
                {
                    "projectId": p.projectId,
                    "genre": p.genre,
                    "mood": p.mood,
                    "duration": p.duration,
                    "status": p.status.value,
                    "progress": p.progress,
                    "previewUrl": p.previewUrl,
                    "finalVideoUrl": p.finalVideoUrl,
                    "createdAt": p.createdAt.isoformat() if p.createdAt else None,
                }
                for p in projects
            ]
        }
    )


@router.post("/project/create")
async def create_project_endpoint(body: CreateProjectRequest, uid: str = Depends(get_current_uid)):
    project = await create_project(
        uid=uid, genre=body.genre, mood=body.mood, prompt=body.prompt, duration=body.duration,
        language=body.language, style=body.style,
    )
    return ok({"projectId": project.projectId, "status": project.status.value})


@router.get("/project/{project_id}")
async def get_project_endpoint(project_id: str, uid: str = Depends(get_current_uid)):
    project = await get_project(project_id=project_id, uid=uid)
    data = {
        "projectId": project.projectId,
        "uid": project.uid,
        "genre": project.genre,
        "mood": project.mood,
        "prompt": project.prompt,
        "duration": project.duration,
        "status": project.status.value,
        "progress": project.progress or STATUS_PROGRESS_MAP.get(project.status, 0),
        "lyrics": project.lyrics.model_dump(mode="json") if project.lyrics else None,
        "audioUrl": project.audio.audioUrl if project.audio else None,
        "subtitleUrl": project.subtitleUrl,
        "previewUrl": project.previewUrl,
        "finalVideoUrl": project.finalVideoUrl,
        "images": [s.model_dump(mode="json") for s in project.images],
        "clips": [s.model_dump(mode="json") for s in project.clips],
        "timeline": [t.model_dump(mode="json") for t in project.timeline],
        "errorCode": project.errorCode,
        "errorMessage": project.errorMessage,
        "retryCount": project.retryCount,
        "createdAt": project.createdAt.isoformat() if project.createdAt else None,
        "updatedAt": project.updatedAt.isoformat() if project.updatedAt else None,
    }
    return ok(data)


@router.get("/project/{project_id}/assets")
async def list_project_assets(project_id: str, uid: str = Depends(get_current_uid)):
    project = await get_project(project_id=project_id, uid=uid)
    assets = await get_asset_repository().list_by_project(project.projectId)
    return ok({"items": [a.model_dump(mode="json") for a in assets]})


@router.post("/project/restart")
async def restart_endpoint(body: dict, uid: str = Depends(get_current_uid)):
    project_id = body.get("projectId")
    step = ProjectStatus(body.get("fromStep", ProjectStatus.GENERATING_LYRICS.value))
    project = await restart_step(project_id=project_id, uid=uid, from_step=step)
    return ok({"projectId": project.projectId, "status": project.status.value})


@router.post("/project/cancel")
async def cancel_endpoint(body: dict, uid: str = Depends(get_current_uid)):
    project_id = body.get("projectId")
    project = await cancel_project(project_id=project_id, uid=uid)
    return ok({"projectId": project.projectId, "status": project.status.value})
