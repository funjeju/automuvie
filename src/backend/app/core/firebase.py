from functools import lru_cache
from pathlib import Path
from typing import Any
from .config import get_settings
from .logger import get_logger

log = get_logger("firebase")


def _resolve_credentials():
    """우선순위:
    1. GOOGLE_APPLICATION_CREDENTIALS=path/to/serviceAccount.json
    2. FIREBASE_PRIVATE_KEY/FIREBASE_CLIENT_EMAIL 개별 env
    """
    from firebase_admin import credentials

    settings = get_settings()
    json_path = settings.google_application_credentials.strip()
    if json_path:
        p = Path(json_path)
        if not p.is_absolute():
            p = (Path.cwd() / p).resolve()
        if p.exists():
            log.info(f"Firebase credentials: file {p}")
            return credentials.Certificate(str(p))
        log.warning(f"GOOGLE_APPLICATION_CREDENTIALS path not found: {p}")

    if settings.firebase_project_id and settings.firebase_private_key and settings.firebase_client_email:
        log.info("Firebase credentials: env vars")
        return credentials.Certificate({
            "type": "service_account",
            "project_id": settings.firebase_project_id,
            "private_key": settings.firebase_private_key.replace("\\n", "\n"),
            "client_email": settings.firebase_client_email,
            "token_uri": "https://oauth2.googleapis.com/token",
        })
    return None


@lru_cache
def init_firebase() -> Any:
    """Firebase Admin SDK 초기화. 자격증명이 없으면 None을 반환해 in-memory로 fallback."""
    settings = get_settings()
    try:
        import firebase_admin

        if firebase_admin._apps:  # type: ignore[attr-defined]
            return firebase_admin.get_app()

        cred = _resolve_credentials()
        if cred is None:
            log.warning("Firebase credentials missing — running in in-memory mode")
            return None

        opts: dict[str, Any] = {}
        if settings.firebase_storage_bucket:
            opts["storageBucket"] = settings.firebase_storage_bucket
        app = firebase_admin.initialize_app(cred, opts)
        log.info(f"Firebase initialized project={settings.firebase_project_id or '(from json)'} bucket={settings.firebase_storage_bucket or '(none)'}")
        return app
    except Exception as e:
        log.error(f"Firebase init failed: {e}")
        return None


def get_firestore():
    init_firebase()
    try:
        from firebase_admin import firestore
        return firestore.client()
    except Exception:
        return None


def get_storage_bucket():
    init_firebase()
    try:
        from firebase_admin import storage
        return storage.bucket()
    except Exception:
        return None
