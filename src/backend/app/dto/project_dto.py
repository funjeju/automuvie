from pydantic import BaseModel, Field
from ..core.constants import MIN_DURATION, MAX_DURATION, MAX_PROMPT_LENGTH


class CreateProjectRequest(BaseModel):
    genre: str = Field(..., min_length=1)
    mood: str = Field(..., min_length=1)
    prompt: str = Field(default="", max_length=MAX_PROMPT_LENGTH)
    duration: int = Field(..., ge=MIN_DURATION, le=MAX_DURATION)
    language: str = Field(default="ko", pattern="^(ko|en|mixed)$")
    style: str = Field(default="", max_length=200)


class ProjectIdRequest(BaseModel):
    projectId: str


class CreateProjectResponse(BaseModel):
    projectId: str
    status: str


class ProjectStatusResponse(BaseModel):
    projectId: str
    status: str
    progress: int
    currentStep: str | None = None


class StatusOnlyResponse(BaseModel):
    status: str


class ProjectDetailResponse(BaseModel):
    projectId: str
    uid: str
    genre: str
    mood: str
    prompt: str
    duration: int
    status: str
    progress: int
    lyrics: dict | None = None
    audioUrl: str | None = None
    subtitleUrl: str | None = None
    previewUrl: str | None = None
    finalVideoUrl: str | None = None
    errorCode: str | None = None
    errorMessage: str | None = None
    retryCount: int = 0
    createdAt: str | None = None
    updatedAt: str | None = None
