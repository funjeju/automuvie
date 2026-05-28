from enum import Enum


class ProjectStatus(str, Enum):
    QUEUED = "queued"
    GENERATING_LYRICS = "generating_lyrics"
    GENERATING_MUSIC = "generating_music"
    GENERATING_IMAGES = "generating_images"
    GENERATING_VIDEO = "generating_video"
    GENERATING_SUBTITLE = "generating_subtitle"
    RENDERING = "rendering"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class RenderStep(str, Enum):
    TIMELINE_ANALYSIS = "timeline_analysis"
    CLIP_SELECTION = "clip_selection"
    TRANSITION = "transition"
    SUBTITLE_BURN = "subtitle_burn"
    AUDIO_SYNC = "audio_sync"
    EXPORT = "export"


class AssetType(str, Enum):
    LYRICS = "lyrics"
    AUDIO = "audio"
    IMAGE = "image"
    VIDEO = "video"
    SUBTITLE = "subtitle"
    PREVIEW = "preview"
    FINAL = "final"


class SectionType(str, Enum):
    VERSE = "verse"
    CHORUS = "chorus"
    BRIDGE = "bridge"


MAX_RETRY_COUNT = 3
MIN_DURATION = 60
MAX_DURATION = 180
MAX_PROMPT_LENGTH = 500
DEFAULT_IMAGES_PER_SECTION = 4
DEFAULT_CLIP_DURATION_RANGE = (8, 15)
DEFAULT_RESOLUTION = (1080, 1920)
PREVIEW_RESOLUTION = (720, 1280)
DEFAULT_FPS = 30
VIDEO_BITRATE = "8M"
AUDIO_BITRATE = "320k"


STATUS_PROGRESS_MAP = {
    ProjectStatus.QUEUED: 0,
    ProjectStatus.GENERATING_LYRICS: 10,
    ProjectStatus.GENERATING_MUSIC: 25,
    ProjectStatus.GENERATING_IMAGES: 45,
    ProjectStatus.GENERATING_VIDEO: 70,
    ProjectStatus.GENERATING_SUBTITLE: 85,
    ProjectStatus.RENDERING: 95,
    ProjectStatus.COMPLETED: 100,
    ProjectStatus.FAILED: 0,
    ProjectStatus.CANCELLED: 0,
}
