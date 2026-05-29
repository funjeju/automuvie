from datetime import datetime
from pydantic import BaseModel, Field
from ..core.constants import ProjectStatus, SectionType


class LyricSection(BaseModel):
    sectionId: str
    type: SectionType
    order: int
    text: str


class Lyrics(BaseModel):
    sections: list[LyricSection]


class TimelineSegment(BaseModel):
    sectionId: str
    start: float
    end: float


class AudioMeta(BaseModel):
    audioUrl: str
    duration: float
    sampleRate: int = 44100


class SectionImages(BaseModel):
    sectionId: str
    images: list[str]


class VideoClip(BaseModel):
    url: str
    duration: float


class SectionClips(BaseModel):
    sectionId: str
    clips: list[VideoClip]


class Project(BaseModel):
    projectId: str
    uid: str
    genre: str
    mood: str
    prompt: str = ""
    duration: int
    language: str = "ko"
    style: str = ""
    status: ProjectStatus = ProjectStatus.QUEUED
    progress: int = 0

    lyrics: Lyrics | None = None
    audio: AudioMeta | None = None
    images: list[SectionImages] = Field(default_factory=list)
    clips: list[SectionClips] = Field(default_factory=list)
    timeline: list[TimelineSegment] = Field(default_factory=list)
    subtitleUrl: str | None = None
    previewUrl: str | None = None
    finalVideoUrl: str | None = None

    errorCode: str | None = None
    errorMessage: str | None = None
    retryCount: int = 0

    createdAt: datetime = Field(default_factory=datetime.utcnow)
    updatedAt: datetime = Field(default_factory=datetime.utcnow)


class RenderJob(BaseModel):
    renderId: str
    projectId: str
    uid: str
    status: str = "queued"
    progress: int = 0
    currentStep: str | None = None
    startedAt: datetime | None = None
    completedAt: datetime | None = None
    retryCount: int = 0
    createdAt: datetime = Field(default_factory=datetime.utcnow)
