from fastapi import HTTPException
from fastapi.responses import JSONResponse


class AppError(Exception):
    code: str = "INTERNAL_ERROR"
    message: str = "내부 오류가 발생했습니다."
    status_code: int = 500

    def __init__(self, message: str | None = None, code: str | None = None, status_code: int | None = None):
        super().__init__(message or self.message)
        if message:
            self.message = message
        if code:
            self.code = code
        if status_code:
            self.status_code = status_code


class ValidationError(AppError):
    code = "VALIDATION_ERROR"
    message = "입력값이 올바르지 않습니다."
    status_code = 400


class NotFoundError(AppError):
    code = "PROJECT_NOT_FOUND"
    message = "프로젝트를 찾을 수 없습니다."
    status_code = 404


class UnauthorizedError(AppError):
    code = "UNAUTHORIZED"
    message = "인증이 필요합니다."
    status_code = 401


class ForbiddenError(AppError):
    code = "FORBIDDEN"
    message = "접근 권한이 없습니다."
    status_code = 403


class PipelineError(AppError):
    code = "PIPELINE_FAILED"
    message = "생성 파이프라인 처리 중 문제가 발생했습니다."
    status_code = 500


class RenderError(AppError):
    code = "RENDER_FAILED"
    message = "렌더링 중 문제가 발생했습니다."
    status_code = 500


def to_response(err: AppError) -> JSONResponse:
    return JSONResponse(
        status_code=err.status_code,
        content={
            "success": False,
            "error": {
                "code": err.code,
                "message": err.message,
            },
        },
    )
