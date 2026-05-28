좋습니다. 4번은 **`04-backend-api-spec.md`**이고, 스타일은 방금 맞춘 것처럼 **소제목 + 서술형**, 단락 붙여서, 개발자가 바로 구현 가능한 수준으로 작성합니다.

# 04-backend-api-spec.md

# Backend API Specification

## API 설계 원칙

본 서비스의 API는 frontend와 backend 간 contract 역할을 수행한다. frontend는 API를 호출하고 상태를 렌더링하는 역할만 담당하며 실제 비즈니스 로직은 backend에서 수행한다. 모든 heavy processing는 async 기반으로 실행하며 synchronous blocking request를 금지한다. API는 REST 기반 구조를 따른다. response format은 모든 endpoint에서 일관성을 유지한다. 생성 요청은 lightweight request 후 queue 처리 방식을 기본 원칙으로 한다.

공통 response 구조:

성공 시:

```json id="y4r1"
{
  "success": true,
  "data": {},
  "message": "ok"
}
```

실패 시:

```json id="x3n2"
{
  "success": false,
  "error": {
    "code": "PROJECT_NOT_FOUND",
    "message": "project not found"
  }
}
```

모든 response는 success field를 포함해야 하며 frontend는 success 기준으로 UI 상태를 판단한다.

## Authentication 정책

모든 API는 Firebase Auth token 기반 인증을 사용한다. 인증이 필요한 endpoint는 Authorization header를 사용한다.

예시:

Authorization: Bearer firebase_token

인증 실패 시:

401 Unauthorized

권한 없는 project 접근 시:

403 Forbidden

## POST /project/create

사용자가 최초 프로젝트를 생성하는 endpoint이다. genre, mood, prompt, duration을 입력받아 project document를 생성하고 queue 등록을 수행한다. 생성 직후 status는 queued 상태를 반환한다.

request:

```json id="d4k2"
{
  "genre": "cinematic emotional",
  "mood": "nostalgic",
  "prompt": "warm memory in lonely city",
  "duration": 120
}
```

validation rule:

* genre required
* mood required
* duration required
* duration min 60
* duration max 180
* prompt max length 500

response:

```json id="j1l2"
{
  "success": true,
  "data": {
    "projectId": "proj_001",
    "status": "queued"
  }
}
```

status code:

200 success
400 validation error
401 unauthorized
500 internal error

## POST /lyrics/generate

특정 project의 lyrics generation을 시작하는 endpoint이다. MVP에서는 자동 pipeline 실행이 기본이므로 internal endpoint 성격을 가진다. manual retry 상황에서 사용 가능하다.

request:

```json id="h9s1"
{
  "projectId": "proj_001"
}
```

response:

```json id="p1d1"
{
  "success": true,
  "data": {
    "status": "generating_lyrics"
  }
}
```

생성 완료 시 저장 데이터:

```json id="c2m1"
{
  "sections": [
    {
      "type": "verse",
      "order": 1,
      "text": "city lights falling softly"
    },
    {
      "type": "chorus",
      "order": 2,
      "text": "stay with me tonight"
    }
  ]
}
```

## POST /music/generate

Lyria 3 Pro 기반 mp3 생성 endpoint이다. lyrics generation 성공 이후 호출 가능하다. 이미 audio 생성 성공 시 재생성 금지한다.

request:

```json id="o1e1"
{
  "projectId": "proj_001"
}
```

response:

```json id="k2t2"
{
  "success": true,
  "data": {
    "status": "generating_music"
  }
}
```

completion result:

```json id="w2r2"
{
  "audioUrl": "/storage/audio/audio.mp3",
  "duration": 118.2
}
```

## POST /image/generate

section 기준 이미지 생성 endpoint이다. GPT Image API 기반으로 동작한다. 각 section마다 기본 4개 variation 생성 규칙을 사용한다.

request:

```json id="f8g3"
{
  "projectId": "proj_001"
}
```

response:

```json id="g2h2"
{
  "success": true,
  "data": {
    "status": "generating_images"
  }
}
```

completion example:

```json id="t2r2"
{
  "sections": [
    {
      "sectionId": "verse_1",
      "images": [
        "image1.png",
        "image2.png",
        "image3.png",
        "image4.png"
      ]
    }
  ]
}
```

## POST /video/generate

Veo 3.1 기반 clip 생성 endpoint이다. lyric section 기준 8~15초 영상 clip을 생성한다. 생성 실패 시 fallback image motion 사용 가능하다.

request:

```json id="q1r1"
{
  "projectId": "proj_001"
}
```

response:

```json id="u2p2"
{
  "success": true,
  "data": {
    "status": "generating_video"
  }
}
```

completion example:

```json id="n3v1"
{
  "clips": [
    {
      "sectionId": "verse_1",
      "url": "clip1.mp4",
      "duration": 8.4
    }
  ]
}
```

## POST /render/start

subtitle generation 이후 최종 렌더링을 시작하는 endpoint이다. ffmpeg-python 기반 single pipeline rendering을 수행한다.

request:

```json id="r1c1"
{
  "projectId": "proj_001"
}
```

response:

```json id="z9m2"
{
  "success": true,
  "data": {
    "status": "rendering"
  }
}
```

render 완료 시:

```json id="m2k2"
{
  "finalVideoUrl": "/storage/render/final.mp4",
  "previewUrl": "/storage/render/preview.mp4"
}
```

## GET /render/status/{projectId}

특정 프로젝트의 render 상태를 조회한다. frontend progress UI는 본 endpoint 또는 realtime listener를 사용한다.

response:

```json id="v1x2"
{
  "success": true,
  "data": {
    "projectId": "proj_001",
    "status": "generating_video",
    "progress": 67,
    "currentStep": "video_generation"
  }
}
```

allowed state:

queued
generating_lyrics
generating_music
generating_images
generating_video
generating_subtitle
rendering
completed
failed
cancelled

## GET /project/{projectId}

프로젝트 전체 데이터를 반환한다. preview 페이지 진입 시 사용한다.

response:

```json id="b7d3"
{
  "success": true,
  "data": {
    "projectId": "proj_001",
    "genre": "cinematic emotional",
    "mood": "nostalgic",
    "lyrics": {},
    "audioUrl": "audio.mp3",
    "subtitleUrl": "subtitle.ass",
    "previewUrl": "preview.mp4",
    "finalVideoUrl": "final.mp4",
    "status": "completed"
  }
}
```

## Retry 정책

모든 generation endpoint는 retry 가능해야 한다. max retry는 3회다. 동일 단계 성공 시 재실행 금지한다. 실패 단계부터 resume을 수행한다.

예:

lyrics success
music success
image failed

→ retry 시 image generation부터 재개

## Error 정책

technical error를 frontend에 직접 노출하지 않는다. frontend에는 사용자 친화적 메시지를 반환한다.

bad:

OpenAI timeout exception

good:

“이미지 생성 중 문제가 발생했습니다. 다시 시도해주세요.”

error response example:

```json id="e2k1"
{
  "success": false,
  "error": {
    "code": "VIDEO_GENERATION_FAILED",
    "message": "영상 생성 중 문제가 발생했습니다."
  }
}
```

## API 설계 원칙

모든 endpoint는 idempotent를 최대한 유지해야 한다. heavy processing는 backend worker에서 수행해야 한다. frontend business logic 금지 원칙을 따른다. request/response schema 변경 시 frontend contract breaking 여부를 반드시 검토한다.
