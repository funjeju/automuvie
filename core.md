# core.md

# AI Music Video Generator — Core Guide

> 이 문서는 프로젝트의 최상위 헌법이다.
> 모든 개발자와 AI(Codex, Cursor, Claude, ChatGPT)는 반드시 이 파일을 먼저 읽고 작업한다.
> docs 내부 문서는 본 파일을 기준으로 구현한다.

---

# 1. 프로젝트 목표

사용자가 장르/분위기(prompt)를 입력하면 AI가 자동으로

* 가사 생성
* 음악 생성(MP3)
* 이미지 생성
* 영상 생성
* 영상 편집
* 노래방 스타일 자막 생성
* 최종 MP4 출력

까지 수행하는 AI 기반 자동 뮤직비디오 생성 플랫폼을 만든다.

최종 목표는 **2~3분 수준의 뮤직비디오를 클릭 몇 번으로 생성하는 것**이다.

---

# 2. 핵심 사용자 플로우

User Input

Genre + Mood + Prompt

↓

Lyrics Generation

Claude API

↓

Music Generation

Lyria 3 Pro API

↓

Image Generation

GPT Image API

↓

Video Generation

Veo 3.1 API

↓

Timeline Analysis

Pydub

↓

Subtitle Timestamp

Whisper API

↓

Video Rendering

ffmpeg-python

↓

Final MP4 Export

---

# 3. MVP 범위

MVP에서는 다음 기능만 구현한다.

## 입력

* 장르
* 분위기
* 자유 prompt
* 곡 길이 (60~180초)

## 출력

* lyrics
* mp3
* preview video
* subtitle.ass
* final.mp4

MVP 제외 기능

* collaborative editing
* community
* template marketplace
* social feed
* advanced editing timeline
* mobile app

---

# 4. 기술 스택 (고정)

## Frontend

* Next.js (App Router)
* TypeScript
* TailwindCSS
* Vercel 배포

## Backend

* FastAPI
* Python 3.12+

## Database

* Firebase Firestore

## Storage

* Firebase Storage

## Authentication

* Firebase Auth

## Rendering

* ffmpeg-python

## Audio Analysis

* pydub

## Subtitle

* Whisper API
* ASS karaoke subtitle

---

# 5. 시스템 아키텍처 원칙

Frontend는 orchestration만 담당한다.

복잡한 비즈니스 로직은 Backend에서 처리한다.

무거운 처리(Render/AI generation)는 async task 기반으로 수행한다.

생성 파이프라인은 resume 가능해야 한다.

모든 단계는 상태 저장(stateful)되어야 한다.

---

# 6. 프로젝트 구조

project-root/

core.md

docs/

src/

frontend/
backend/

assets/

temp/

output/

tests/

---

# 7. 생성 파이프라인 규칙

반드시 아래 순서를 따른다.

1. Lyrics Generation
2. Music Generation
3. Image Generation
4. Video Generation
5. Audio Timing Analysis
6. Subtitle Timestamp
7. Video Rendering
8. Final Export

단계를 건너뛰는 구현 금지.

---

# 8. 단계별 출력 계약(Contract)

모든 단계는 결과물을 저장한다.

## lyrics

output:

lyrics.json

```json
{
  "sections": [
    {
      "type": "verse",
      "text": "...",
      "order": 1
    }
  ]
}
```

## music

output:

audio.mp3

metadata.json

## image

output:

images/

section별 이미지 저장

## video

output:

clips/

section별 clip 저장

## subtitle

output:

subtitle.ass

## render

output:

draft.mp4

final.mp4

---

# 9. 상태(Status) 규칙

모든 project는 상태를 가진다.

allowed status:

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

---

# 10. 실패 처리 규칙

모든 단계는 retry 가능해야 한다.

3회 실패 시 failed 처리.

resume 지원 필수.

예:

music 생성 성공
video 생성 실패

→ music부터 다시 생성 금지
→ 실패한 단계부터 재시작

---

# 11. 캐시 규칙

비용 절감을 위해 캐시 사용.

동일 prompt + 동일 seed이면 재사용.

캐시 대상:

* lyrics
* music
* image
* video

---

# 12. 렌더링 규칙

반드시 ffmpeg-python 사용.

CLI 문자열 하드코딩 금지.

기본 출력:

* 1080x1920
* mp4
* H264
* AAC

transition:

* fade in
* fade out
* cross dissolve

subtitle:

ASS karaoke style mandatory

---

# 13. 개발 규칙

## Frontend

* TypeScript strict mode
* server action 우선
* component 분리

## Backend

* typing 필수
* async 우선
* service layer 사용
* repository pattern 사용

---

# 14. 금지사항

금지:

* hardcoding
* blocking API call
* business logic in frontend
* ffmpeg shell string 난립
* temp 파일 방치

---

# 15. 환경 변수 규칙

.env 분리

FRONTEND_ENV

BACKEND_ENV

API key 하드코딩 금지

---

# 16. 성공 기준

사용자가

1. prompt 입력
2. 생성 버튼 클릭
3. 2~3분 뮤직비디오 자동 생성
4. final.mp4 다운로드

가 가능해야 한다.

이 기준을 만족하면 MVP 완료로 본다.

---

# 17. docs 문서 작성 규칙

docs 내부 문서는 반드시 본 core.md 규칙을 따른다.

모든 문서는 아래 원칙을 지킨다.

원칙:

1. 개발자가 바로 구현 가능한 수준으로 작성
2. 추상 설명 금지
3. 실제 request/response 예시 포함
4. JSON schema 포함
5. 성공/실패 케이스 작성
6. 입력(input) / 출력(output) 명확화
7. 상태(state) 정의
8. edge case 포함

모든 md 파일은 다음 구조를 가진다.

* 목적(Objective)
* 범위(Scope)
* 기능(Function)
* Input
* Output
* State
* API
* Error Handling
* Example
* Implementation Rule

---

# 18. docs 파일 정의

## 01-product-spec.md

목적:

서비스 요구사항(PRD) 정의

반드시 포함:

* 서비스 목표
* 사용자 시나리오
* 핵심 플로우
* MVP 범위
* 제외 범위
* 화면별 기능
* 유저 행동 흐름
* 입력/출력 정의
* success metric

산출물:

개발자가 제품 요구사항을 이해할 수 있어야 함

---

## 02-system-architecture.md

목적:

전체 시스템 구조 설계

반드시 포함:

* 시스템 구조도
* frontend/backend 관계
* async flow
* render lifecycle
* queue 구조
* retry 전략
* resume 전략
* storage 흐름
* state transition

필수 포함:

sequence diagram

예시:

frontend
→ backend
→ ai pipeline
→ storage
→ render
→ output

산출물:

개발자가 전체 구조를 구현 가능해야 함

---

## 03-frontend-ui-ux-design.md

목적:

UI/UX 설계

반드시 포함:

페이지:

1. Landing
2. Generate
3. Progress
4. Preview
5. Download

필수 포함:

* wireframe
* component tree
* loading state
* failed state
* progress UI
* mobile UI
* responsive rule
* typography
* spacing
* color system

디자인 방향:

cinematic
modern
dark-first
minimal

산출물:

디자이너 없이 구현 가능해야 함

---

## 04-backend-api-spec.md

목적:

API 구현 명세

반드시 포함:

endpoint:

POST /project/create
POST /lyrics/generate
POST /music/generate
POST /image/generate
POST /video/generate
POST /render/start
GET /render/status
GET /project/{id}

필수 포함:

* request schema
* response schema
* status code
* retry policy
* auth requirement
* error response

예시 JSON 필수

산출물:

백엔드 개발자가 API 구현 가능해야 함

---

## 05-ai-generation-pipeline.md

목적:

AI 생성 엔진 설계

반드시 포함:

step1:

Claude lyric generation

* Verse
* Chorus
* Bridge
* tone control

step2:

Lyria

* mp3 generation
* metadata

step3:

GPT Image

* per section image generation
* style consistency
* seed handling

step4:

Veo

* clip generation
* motion prompt
* duration

step5:

Whisper

* timestamp extraction

필수 포함:

* cache rule
* retry rule
* fallback strategy
* input/output contract

산출물:

AI pipeline 구현 가능해야 함

---

## 06-video-rendering-engine.md

목적:

영상 합성 엔진 구현

반드시 포함:

* pydub timing
* clip repeat logic
* transition
* fade in/out
* concat
* subtitle burn
* karaoke effect
* ffmpeg-python graph

반드시 명시:

resolution
fps
codec
audio bitrate
video bitrate

필수:

실제 ffmpeg-python flow 예시

산출물:

영상 엔진 구현 가능해야 함

---

## 07-database-schema-firebase.md

목적:

Firestore schema 설계

반드시 포함:

collections:

users
projects
renders
assets

각 document schema 포함

예시:

project:

id
uid
prompt
genre
status
lyrics
audioUrl
progress
timestamps
createdAt

storage path rule 포함

security rule 포함

산출물:

DB 바로 생성 가능해야 함

---

## 08-deployment-vercel-firebase.md

목적:

배포 가이드

반드시 포함:

* Vercel deploy
* Firebase setup
* env structure
* production build
* CI/CD
* secret management
* logging
* monitoring

필수:

환경변수 예시

산출물:

신입 개발자도 배포 가능해야 함

---

## 09-development-rules.md

목적:

개발 규칙 통일

반드시 포함:

typescript:

* strict true

python:

* typing required
* async required

architecture:

* service layer
* repository pattern
* DTO pattern

금지사항:

* hardcoding
* duplicated logic
* blocking api call
* business logic in frontend

필수:

folder convention
naming convention
test rule
commit convention

산출물:

코드 스타일 일관성 유지 가능해야 함

---

# 19. 최종 원칙

docs 내부 md 파일은

“설명 문서”

가 아니라

“바로 구현 가능한 실행 문서”

여야 한다.

모든 문서는

"개발자가 질문 없이 바로 구현 가능한가?"

기준으로 작성한다.
