from datetime import datetime
from typing import Protocol
from pydantic import BaseModel, Field
from ..core.firebase import get_firestore
from ..core.constants import AssetType


class AssetMeta(BaseModel):
    assetId: str
    projectId: str
    uid: str
    assetType: AssetType
    sectionId: str | None = None
    url: str
    duration: float | None = None
    width: int | None = None
    height: int | None = None
    createdAt: datetime = Field(default_factory=datetime.utcnow)


class AssetRepository(Protocol):
    async def save(self, asset: AssetMeta) -> AssetMeta: ...
    async def list_by_project(self, project_id: str) -> list[AssetMeta]: ...


class InMemoryAssetRepository:
    def __init__(self) -> None:
        self._store: dict[str, AssetMeta] = {}

    async def save(self, asset: AssetMeta) -> AssetMeta:
        self._store[asset.assetId] = asset
        return asset

    async def list_by_project(self, project_id: str) -> list[AssetMeta]:
        return [a for a in self._store.values() if a.projectId == project_id]


class FirestoreAssetRepository:
    COLLECTION = "assets"

    def __init__(self) -> None:
        self._client = get_firestore()
        self._fallback = InMemoryAssetRepository()

    def _col(self):
        return self._client.collection(self.COLLECTION) if self._client else None

    async def save(self, asset: AssetMeta) -> AssetMeta:
        if not self._client:
            return await self._fallback.save(asset)
        self._col().document(asset.assetId).set(asset.model_dump(mode="json"))
        return asset

    async def list_by_project(self, project_id: str) -> list[AssetMeta]:
        if not self._client:
            return await self._fallback.list_by_project(project_id)
        snaps = self._col().where("projectId", "==", project_id).stream()
        return [AssetMeta.model_validate(s.to_dict()) for s in snaps]


_asset_repo_singleton: AssetRepository | None = None


def get_asset_repository() -> AssetRepository:
    global _asset_repo_singleton
    if _asset_repo_singleton is None:
        _asset_repo_singleton = FirestoreAssetRepository()
    return _asset_repo_singleton
