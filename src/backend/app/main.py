from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from .api.v1.router import api_router
from .core.config import get_settings
from .core.errors import AppError, to_response
from .core.firebase import init_firebase
from .core.logger import get_logger
from .workers.task_queue import get_task_queue

log = get_logger("main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_firebase()
    queue = get_task_queue()
    await queue.start()
    log.info("app startup complete")
    try:
        yield
    finally:
        await queue.stop()
        log.info("app shutdown complete")


app = FastAPI(
    title="AI Music Video Generator",
    version="0.1.0",
    lifespan=lifespan,
)

settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError):
    return to_response(exc)


@app.exception_handler(Exception)
async def unknown_error_handler(request: Request, exc: Exception):
    log.exception(f"unhandled: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": {"code": "INTERNAL_ERROR", "message": "내부 오류가 발생했습니다."},
        },
    )


@app.get("/health")
async def health():
    return {"success": True, "data": {"status": "ok"}, "message": "ok"}


# 로컬 개발 모드 — generated asset을 브라우저에 직접 서빙한다.
# (Firebase Storage가 설정되면 storage URL이 사용되므로 본 mount는 fallback 용도)
output_root = Path(settings.output_dir).resolve()
output_root.mkdir(parents=True, exist_ok=True)
app.mount("/static/projects", StaticFiles(directory=str(output_root)), name="generated_assets")


app.include_router(api_router, prefix="/api/v1")
