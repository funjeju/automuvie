import base64
import struct
import zlib
from pathlib import Path
from ...models.domain import Lyrics, SectionImages
from ...repositories.storage_repository import get_storage_repository
from ...core.constants import DEFAULT_IMAGES_PER_SECTION, DEFAULT_RESOLUTION
from ...core.config import get_settings
from ...core.logger import get_logger

log = get_logger("image")


def _gradient_png(width: int, height: int, top: tuple[int, int, int], bottom: tuple[int, int, int]) -> bytes:
    """순수 Python으로 PNG 인코딩한다 (Pillow 미설치 환경 대응)."""

    def chunk(tag: bytes, data: bytes) -> bytes:
        return (
            struct.pack(">I", len(data))
            + tag
            + data
            + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
        )

    sig = b"\x89PNG\r\n\x1a\n"
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    raw = bytearray()
    for y in range(height):
        ratio = y / max(height - 1, 1)
        r = int(top[0] + (bottom[0] - top[0]) * ratio)
        g = int(top[1] + (bottom[1] - top[1]) * ratio)
        b = int(top[2] + (bottom[2] - top[2]) * ratio)
        raw.append(0)
        raw += bytes((r, g, b)) * width
    idat = zlib.compress(bytes(raw), 9)
    return sig + chunk(b"IHDR", ihdr) + chunk(b"IDAT", idat) + chunk(b"IEND", b"")


_MOOD_PALETTE: dict[str, tuple[tuple[int, int, int], tuple[int, int, int]]] = {
    "nostalgic": ((20, 18, 48), (138, 77, 255)),
    "energetic": ((255, 90, 60), (255, 220, 100)),
    "calm": ((20, 60, 80), (160, 220, 220)),
    "dark": ((9, 11, 26), (90, 50, 140)),
}


def _palette_for(mood: str, idx: int) -> tuple[tuple[int, int, int], tuple[int, int, int]]:
    base = _MOOD_PALETTE.get(mood.lower(), ((30, 20, 60), (217, 70, 239)))
    shift = (idx * 17) % 60
    top = tuple(min(255, max(0, c + shift)) for c in base[0])
    bottom = tuple(min(255, max(0, c - shift)) for c in base[1])
    return top, bottom  # type: ignore[return-value]


class MockImageProvider:
    async def generate(self, *, project_id: str, lyrics: Lyrics, genre: str, mood: str) -> list[SectionImages]:
        storage = get_storage_repository()
        w, h = DEFAULT_RESOLUTION
        out: list[SectionImages] = []
        for sec in lyrics.sections:
            urls: list[str] = []
            for i in range(DEFAULT_IMAGES_PER_SECTION):
                filename = f"{sec.sectionId}_{i+1}.png"
                local = Path(storage.local_path(project_id, "images", filename))
                local.parent.mkdir(parents=True, exist_ok=True)
                top, bottom = _palette_for(mood, hash((sec.sectionId, i)) & 0xFFFF)
                local.write_bytes(_gradient_png(w, h, top, bottom))
                urls.append(storage.upload(project_id, "images", filename, str(local)))
            out.append(SectionImages(sectionId=sec.sectionId, images=urls))
        return out


class GPTImageProvider:
    async def generate(self, *, project_id: str, lyrics: Lyrics, genre: str, mood: str) -> list[SectionImages]:
        try:
            from openai import OpenAI
        except Exception:
            log.warning("openai SDK 미설치 — mock fallback")
            return await MockImageProvider().generate(project_id=project_id, lyrics=lyrics, genre=genre, mood=mood)

        settings = get_settings()
        if not settings.openai_api_key:
            return await MockImageProvider().generate(project_id=project_id, lyrics=lyrics, genre=genre, mood=mood)

        client = OpenAI(api_key=settings.openai_api_key)
        storage = get_storage_repository()
        out: list[SectionImages] = []
        style = f"cinematic vertical 9:16, {genre}, {mood}, consistent palette, premium film grade"
        for sec in lyrics.sections:
            urls: list[str] = []
            for i in range(DEFAULT_IMAGES_PER_SECTION):
                prompt = f"{style}. Scene: {sec.text}. Variation {i+1}."
                resp = client.images.generate(model="gpt-image-1", prompt=prompt, size="1024x1792", n=1)
                b64 = resp.data[0].b64_json  # type: ignore[union-attr]
                filename = f"{sec.sectionId}_{i+1}.png"
                local = Path(storage.local_path(project_id, "images", filename))
                local.write_bytes(base64.b64decode(b64))
                urls.append(storage.upload(project_id, "images", filename, str(local)))
            out.append(SectionImages(sectionId=sec.sectionId, images=urls))
        return out


def get_image_provider():
    settings = get_settings()
    if settings.image_provider == "live":
        return GPTImageProvider()
    return MockImageProvider()
