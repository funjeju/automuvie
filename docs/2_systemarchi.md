맞습니다. 방금 건 UI 스펙 문서 느낌으로 길게 쓴 거고, 당신이 말한 **“소제목 + 서술형” 스타일**이 아니었습니다. 수정해서 이후 문서는 그 스타일로 맞추겠습니다.

두 번째 md는 **`02-system-architecture.md`** 입니다. 개발자가 바로 구현 들어갈 수 있도록, 소제목+서술형 중심, 단락 최소화해서 작성합니다.

# 02-system-architecture.md

# System Architecture

## 시스템 구조

본 서비스는 Next.js 기반 프론트엔드와 FastAPI 기반 백엔드로 구성되며 Firebase를 데이터 저장 및 인증 계층으로 사용한다. Frontend는 orchestration과 UI rendering만 담당하고, 실제 생성 로직은 Backend에서 처리한다. 무거운 AI 생성 작업과 렌더링은 반드시 비동기(async) task 기반으로 처리하며 사용자는 실시간 진행률(progress)을 확인할 수 있어야 한다.

전체 구조는 아래 흐름을 따른다.

User → Next.js Frontend → FastAPI Backend → AI APIs(Claude, Lyria, GPT Image, Veo, Whisper) → Firebase Storage → ffmpeg-python Rendering → Final MP4 Output

Frontend는 API 호출과 상태 조회만 담당하며 business logic은 절대 포함하지 않는다. Backend는 workflow orchestration, retry, cache, render lifecycle, asset generation을 담당한다.

## 시스템 데이터 흐름

사용자가 genre, mood, prompt, duration을 입력하면 frontend는 project 생성 API를 호출한다. Backend는 project document를 Firestore에 생성하고 상태(status)를 queued로 기록한다. 이후 backend worker가 pipeline을 시작한다. pipeline은 lyrics generation → music generation → image generation → video generation → subtitle generation → rendering 순서로 진행된다. 각 단계 종료 시 Firestore status를 갱신하며 frontend는 polling 또는 realtime listener를 통해 상태를 업데이트한다. 모든 생성물은 Firebase Storage에 저장되며 final.mp4 생성 완료 시 completed 상태로 변경된다.

Flow:

Prompt Input → Create Project → Queue Task → Generate Lyrics → Generate Music → Generate Images → Generate Video Clips → Extract Subtitle Timestamp → Render Video → Export Final MP4

## Frontend 구조

Frontend는 Next.js App Router 기반으로 구현한다. 역할은 입력 UI, 진행률 UI, preview UI, 다운로드 UI 제공이다. frontend는 API orchestration 역할만 수행하며 heavy processing 금지, render 금지, ffmpeg 처리 금지 원칙을 따른다. 생성 상태는 Firestore realtime subscription 또는 polling으로 관리한다.

Frontend responsibility:

* prompt input
* project creation
* render status display
* asset preview
* download action

금지사항:

* business logic
* ffmpeg execution
* ai processing
* storage orchestration

## Backend 구조

Backend는 FastAPI 기반으로 구현한다. 모든 pipeline orchestration은 backend에서 수행한다. backend는 task state 관리, retry, cache, asset generation, storage upload, rendering orchestration을 담당한다. API는 lightweight를 유지하고 heavy task는 worker에서 실행한다.

Backend responsibility:

* pipeline orchestration
* ai generation
* subtitle generation
* render lifecycle
* cache management
* project status update
* firebase sync

## Queue 구조

모든 생성 작업은 async queue 기반으로 실행한다. request thread에서 직접 생성 금지 원칙을 따른다. create project 요청이 들어오면 backend는 job을 enqueue한다. worker는 queue를 읽고 순차적으로 처리한다. queue는 resume 가능해야 하며 실패한 단계부터 재실행 가능해야 한다.

queue lifecycle:

queued → processing → completed

실패 시:

failed

사용자 취소 시:

cancelled

retry rule:

max retry = 3

timeout 발생 시 exponential backoff 적용.

## Pipeline 구조

Pipeline은 반드시 아래 순서를 따른다.

1. Claude API lyric generation
2. Lyria 3 Pro music generation
3. GPT Image section image generation
4. Veo 3.1 clip generation
5. Whisper timestamp extraction
6. ffmpeg-python rendering
7. final.mp4 export

단계 skip 금지. 성공한 단계 재실행 금지. 실패 시 실패 단계부터 resume 가능해야 한다.

예시:

lyrics success
music success
video failed

→ resume 시 video generation부터 시작

## 상태 관리 구조

모든 프로젝트는 Firestore에 상태를 가진다. frontend는 해당 상태를 기준으로 진행률 UI를 표시한다.

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

각 상태는 timestamp를 저장해야 하며 error message 저장 가능해야 한다.

example:

```json id="c4j7s1"
{
  "projectId": "project_001",
  "status": "generating_video",
  "progress": 67,
  "updatedAt": "2026-05-28T21:00:00Z"
}
```

## Storage 구조

모든 생성 결과물은 Firebase Storage 저장을 기본으로 한다. temp 결과물은 backend local temp directory 사용 후 업로드 완료 시 삭제한다.

storage rule:

/projects/{projectId}/lyrics/
/projects/{projectId}/audio/
/projects/{projectId}/images/
/projects/{projectId}/clips/
/projects/{projectId}/subtitle/
/projects/{projectId}/render/

final output:

final.mp4

preview.mp4

subtitle.ass

metadata.json

## Cache 구조

비용 최적화를 위해 동일 입력값은 cache 재사용을 허용한다. cache key는 genre + mood + prompt + duration + seed 기준 생성한다. 동일 조건일 경우 재생성보다 cached asset 우선 사용한다.

cache target:

* lyrics
* music
* image
* video

subtitle과 render 결과는 cache 대상 제외.

## 에러 처리 구조

모든 단계는 retry 가능해야 하며 실패 시 backend가 상태를 failed로 변경한다. frontend는 technical message 노출 금지 원칙을 따른다.

bad:

API timeout

good:

“영상 생성 중 문제가 발생했습니다. 다시 시도해주세요.”

resume 가능한 경우 retry button 제공.

## 보안 구조

API key는 frontend 저장 금지. 모든 key는 backend env에서만 관리한다. Firebase security rule 적용 필수. 인증되지 않은 사용자의 project 접근 금지. storage 접근은 uid 기준 제한한다.

## 아키텍처 원칙

본 서비스는 “Frontend Thin, Backend Heavy” 원칙을 따른다. Frontend는 보여주는 역할, Backend는 생성하는 역할을 담당한다. 모든 무거운 작업은 backend에서 async 처리하며 모든 생성 단계는 resume 가능하고 stateful 해야 한다.
