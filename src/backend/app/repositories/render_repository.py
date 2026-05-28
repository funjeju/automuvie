from datetime import datetime
from typing import Protocol
from ..core.firebase import get_firestore
from ..models.domain import RenderJob


class RenderRepository(Protocol):
    async def create(self, job: RenderJob) -> RenderJob: ...
    async def update_step(self, render_id: str, step: str, progress: int) -> None: ...
    async def mark_completed(self, render_id: str) -> None: ...
    async def mark_failed(self, render_id: str) -> None: ...
    async def get(self, render_id: str) -> RenderJob | None: ...


class InMemoryRenderRepository:
    def __init__(self) -> None:
        self._store: dict[str, RenderJob] = {}

    async def create(self, job: RenderJob) -> RenderJob:
        job.createdAt = datetime.utcnow()
        self._store[job.renderId] = job
        return job

    async def update_step(self, render_id: str, step: str, progress: int) -> None:
        job = self._store.get(render_id)
        if job:
            job.currentStep = step
            job.progress = progress

    async def mark_completed(self, render_id: str) -> None:
        job = self._store.get(render_id)
        if job:
            job.status = "completed"
            job.progress = 100
            job.completedAt = datetime.utcnow()

    async def mark_failed(self, render_id: str) -> None:
        job = self._store.get(render_id)
        if job:
            job.status = "failed"
            job.retryCount += 1

    async def get(self, render_id: str) -> RenderJob | None:
        return self._store.get(render_id)


class FirestoreRenderRepository:
    COLLECTION = "renders"

    def __init__(self) -> None:
        self._client = get_firestore()
        self._fallback = InMemoryRenderRepository()

    def _col(self):
        return self._client.collection(self.COLLECTION) if self._client else None

    async def create(self, job: RenderJob) -> RenderJob:
        if not self._client:
            return await self._fallback.create(job)
        job.createdAt = datetime.utcnow()
        self._col().document(job.renderId).set(job.model_dump(mode="json"))
        return job

    async def update_step(self, render_id: str, step: str, progress: int) -> None:
        if not self._client:
            await self._fallback.update_step(render_id, step, progress)
            return
        self._col().document(render_id).update({"currentStep": step, "progress": progress})

    async def mark_completed(self, render_id: str) -> None:
        if not self._client:
            await self._fallback.mark_completed(render_id)
            return
        self._col().document(render_id).update(
            {"status": "completed", "progress": 100, "completedAt": datetime.utcnow().isoformat()}
        )

    async def mark_failed(self, render_id: str) -> None:
        if not self._client:
            await self._fallback.mark_failed(render_id)
            return
        doc = self._col().document(render_id)
        snap = doc.get()
        retry = (snap.to_dict() or {}).get("retryCount", 0) + 1 if snap.exists else 1
        doc.update({"status": "failed", "retryCount": retry})

    async def get(self, render_id: str) -> RenderJob | None:
        if not self._client:
            return await self._fallback.get(render_id)
        snap = self._col().document(render_id).get()
        if not snap.exists:
            return None
        return RenderJob.model_validate(snap.to_dict())


_render_repo_singleton: RenderRepository | None = None


def get_render_repository() -> RenderRepository:
    global _render_repo_singleton
    if _render_repo_singleton is None:
        _render_repo_singleton = FirestoreRenderRepository()
    return _render_repo_singleton
