from datetime import datetime
from typing import Protocol
from ..models.domain import Project
from ..core.constants import ProjectStatus, STATUS_PROGRESS_MAP
from ..core.firebase import get_firestore
from ..core.logger import get_logger

log = get_logger("project_repo")


class ProjectRepository(Protocol):
    async def create(self, project: Project) -> Project: ...
    async def get(self, project_id: str) -> Project | None: ...
    async def update(self, project: Project) -> Project: ...
    async def list_by_uid(self, uid: str, limit: int = 50) -> list[Project]: ...
    async def set_status(
        self, project_id: str, status: ProjectStatus, *, error_code: str | None = None, error_message: str | None = None
    ) -> None: ...


class InMemoryProjectRepository:
    """개발용 in-memory 저장소. Firestore unavailable 시 fallback."""

    def __init__(self) -> None:
        self._store: dict[str, Project] = {}

    async def create(self, project: Project) -> Project:
        project.createdAt = datetime.utcnow()
        project.updatedAt = project.createdAt
        self._store[project.projectId] = project
        return project

    async def get(self, project_id: str) -> Project | None:
        return self._store.get(project_id)

    async def update(self, project: Project) -> Project:
        project.updatedAt = datetime.utcnow()
        self._store[project.projectId] = project
        return project

    async def list_by_uid(self, uid: str, limit: int = 50) -> list[Project]:
        items = [p for p in self._store.values() if p.uid == uid]
        items.sort(key=lambda p: p.createdAt, reverse=True)
        return items[:limit]

    async def set_status(
        self, project_id: str, status: ProjectStatus, *, error_code: str | None = None, error_message: str | None = None
    ) -> None:
        project = self._store.get(project_id)
        if not project:
            return
        project.status = status
        project.progress = STATUS_PROGRESS_MAP.get(status, project.progress)
        project.errorCode = error_code
        project.errorMessage = error_message
        project.updatedAt = datetime.utcnow()


class FirestoreProjectRepository:
    """Firestore 구현. firestore client 없으면 InMemory로 fallback."""

    COLLECTION = "projects"

    def __init__(self) -> None:
        self._client = get_firestore()
        self._fallback = InMemoryProjectRepository()

    def _col(self):
        return self._client.collection(self.COLLECTION) if self._client else None

    async def create(self, project: Project) -> Project:
        if not self._client:
            return await self._fallback.create(project)
        project.createdAt = datetime.utcnow()
        project.updatedAt = project.createdAt
        self._col().document(project.projectId).set(project.model_dump(mode="json"))
        return project

    async def get(self, project_id: str) -> Project | None:
        if not self._client:
            return await self._fallback.get(project_id)
        doc = self._col().document(project_id).get()
        if not doc.exists:
            return None
        return Project.model_validate(doc.to_dict())

    async def update(self, project: Project) -> Project:
        if not self._client:
            return await self._fallback.update(project)
        project.updatedAt = datetime.utcnow()
        self._col().document(project.projectId).set(project.model_dump(mode="json"))
        return project

    async def list_by_uid(self, uid: str, limit: int = 50) -> list[Project]:
        if not self._client:
            return await self._fallback.list_by_uid(uid, limit)
        snaps = self._col().where("uid", "==", uid).order_by("createdAt", direction="DESCENDING").limit(limit).stream()
        return [Project.model_validate(s.to_dict()) for s in snaps]

    async def set_status(
        self, project_id: str, status: ProjectStatus, *, error_code: str | None = None, error_message: str | None = None
    ) -> None:
        if not self._client:
            await self._fallback.set_status(project_id, status, error_code=error_code, error_message=error_message)
            return
        self._col().document(project_id).update({
            "status": status.value,
            "progress": STATUS_PROGRESS_MAP.get(status, 0),
            "errorCode": error_code,
            "errorMessage": error_message,
            "updatedAt": datetime.utcnow().isoformat(),
        })


_repo_singleton: ProjectRepository | None = None


def get_project_repository() -> ProjectRepository:
    global _repo_singleton
    if _repo_singleton is None:
        _repo_singleton = FirestoreProjectRepository()
    return _repo_singleton
