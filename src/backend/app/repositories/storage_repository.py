import os
import shutil
from pathlib import Path
from ..core.config import get_settings
from ..core.firebase import get_storage_bucket
from ..core.logger import get_logger

log = get_logger("storage_repo")


class StorageRepository:
    """
    Firebase Storage upload + local mirroring.
    storage path rule: /projects/{projectId}/{group}/{filename}
    """

    def __init__(self) -> None:
        self.settings = get_settings()
        self.bucket = get_storage_bucket()
        self.local_root = Path(self.settings.output_dir).resolve()
        self.local_root.mkdir(parents=True, exist_ok=True)

    def _local_path(self, project_id: str, group: str, filename: str) -> Path:
        path = self.local_root / project_id / group
        path.mkdir(parents=True, exist_ok=True)
        return path / filename

    def write_text(self, project_id: str, group: str, filename: str, content: str) -> str:
        local = self._local_path(project_id, group, filename)
        local.write_text(content, encoding="utf-8")
        return self.upload(project_id, group, filename, str(local))

    def write_bytes(self, project_id: str, group: str, filename: str, content: bytes) -> str:
        local = self._local_path(project_id, group, filename)
        local.write_bytes(content)
        return self.upload(project_id, group, filename, str(local))

    def upload(self, project_id: str, group: str, filename: str, source_path: str) -> str:
        """파일 업로드 후 브라우저 접근 가능한 URL 반환.
        Firebase Storage가 설정되어 있으면 public URL을, 아니면 backend가 서빙하는
        /static/projects/... URL을 반환한다. (StaticFiles mount 기준)
        """
        target_local = self._local_path(project_id, group, filename)
        if Path(source_path).resolve() != target_local.resolve():
            shutil.copy2(source_path, target_local)

        remote = f"projects/{project_id}/{group}/{filename}"
        if not self.bucket:
            return f"{self.settings.api_base_url.rstrip('/')}/static/{remote}"

        blob = self.bucket.blob(remote)
        blob.upload_from_filename(str(target_local))
        try:
            blob.make_public()
            return blob.public_url
        except Exception:
            return f"gs://{self.bucket.name}/{remote}"

    def local_path(self, project_id: str, group: str, filename: str) -> str:
        return str(self._local_path(project_id, group, filename))


_storage_singleton: StorageRepository | None = None


def get_storage_repository() -> StorageRepository:
    global _storage_singleton
    if _storage_singleton is None:
        _storage_singleton = StorageRepository()
    return _storage_singleton
