from fastapi import Depends, Header
from .errors import UnauthorizedError


async def get_current_uid(authorization: str | None = Header(default=None)) -> str:
    """
    MVP: Authorization: Bearer <firebase_token>
    Token verification은 firebase_admin.auth로 처리한다.
    초기 개발 단계에서는 mock token (`dev:<uid>`)을 허용한다.
    """
    if not authorization:
        raise UnauthorizedError()

    if not authorization.lower().startswith("bearer "):
        raise UnauthorizedError(message="잘못된 인증 헤더 형식입니다.")

    token = authorization.split(" ", 1)[1].strip()
    if not token:
        raise UnauthorizedError()

    if token.startswith("dev:"):
        return token[4:] or "dev_user"

    try:
        from firebase_admin import auth as fb_auth
        decoded = fb_auth.verify_id_token(token)
        return decoded["uid"]
    except Exception:
        raise UnauthorizedError(message="유효하지 않은 토큰입니다.")


CurrentUid = Depends(get_current_uid)
