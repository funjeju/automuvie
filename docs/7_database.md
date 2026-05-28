# 07-database-schema-firebase.md

# Firebase Database Schema

## 데이터베이스 설계 원칙

본 서비스는 Firebase Firestore를 primary database로 사용한다. Firestore는 project 중심 구조를 따른다. 모든 생성 과정은 project document를 기준으로 상태(state)를 관리하며 생성 결과물(asset)은 Firebase Storage에 저장한다. Firestore는 metadata, state, progress tracking을 담당하고 Storage는 실제 binary asset(mp3, image, video, subtitle)을 저장한다. 모든 schema는 resume 가능한 pipeline을 기준으로 설계한다. document 구조는 deterministic 해야 하며 nullable field 남용을 금지한다.

Firestore collection:

users
projects
renders
assets

Storage:

/projects/{projectId}/

모든 collection은 uid 기반 접근 제어를 적용한다.

## Users Collection

users collection은 사용자 메타데이터와 usage 상태를 저장한다. 인증은 Firebase Auth 기반이며 document id는 uid와 동일하게 사용한다.

path:

users/{uid}

schema:

```json id="u1s2"
{
  "uid": "uid_001",
  "email": "user@email.com",
  "displayName": "user",
  "photoUrl": "profile.png",
  "plan": "free",
  "credits": 30,
  "createdAt": "timestamp",
  "updatedAt": "timestamp",
  "lastLoginAt": "timestamp"
}
```

field rule:

uid:

required

plan:

free | pro | enterprise

credits:

remaining generation count

createdAt:

server timestamp mandatory

사용자 삭제 시 project soft delete만 허용한다.

## Projects Collection

projects collection은 서비스 핵심 entity다. 하나의 프로젝트는 하나의 뮤직비디오 생성 단위를 의미한다. 모든 pipeline 상태는 project document 기준으로 저장한다.

path:

projects/{projectId}

schema:

```json id="a2k1"
{
  "projectId": "proj_001",
  "uid": "uid_001",
  "genre": "cinematic emotional",
  "mood": "nostalgic",
  "prompt": "warm memory in lonely city",
  "duration": 120,
  "status": "generating_video",
  "progress": 67,
  "lyricsId": "lyrics_001",
  "renderId": "render_001",
  "audioUrl": "audio.mp3",
  "subtitleUrl": "subtitle.ass",
  "previewUrl": "preview.mp4",
  "finalVideoUrl": "final.mp4",
  "errorCode": null,
  "errorMessage": null,
  "retryCount": 1,
  "createdAt": "timestamp",
  "updatedAt": "timestamp"
}
```

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

progress range:

0~100

rule:

project document는 pipeline source of truth 역할을 수행한다.

## Assets Collection

assets collection은 생성된 이미지, 영상, subtitle, metadata 정보를 저장한다. binary file 자체는 storage에 저장하고 firestore는 metadata만 관리한다.

path:

assets/{assetId}

schema:

```json id="m3k2"
{
  "assetId": "asset_001",
  "projectId": "proj_001",
  "uid": "uid_001",
  "assetType": "image",
  "sectionId": "verse_1",
  "url": "storage/image1.png",
  "duration": 8.2,
  "width": 1080,
  "height": 1920,
  "createdAt": "timestamp"
}
```

allowed assetType:

lyrics
audio
image
video
subtitle
preview
final

sectionId는 lyric section 기준으로 저장한다.

예시:

verse_1
chorus_1
bridge_1

rule:

binary file 저장 금지. metadata only.

## Renders Collection

renders collection은 rendering lifecycle을 저장한다. render progress 추적과 resume 처리를 위한 collection이다.

path:

renders/{renderId}

schema:

```json id="r8n2"
{
  "renderId": "render_001",
  "projectId": "proj_001",
  "uid": "uid_001",
  "status": "rendering",
  "progress": 74,
  "currentStep": "subtitle_burn",
  "startedAt": "timestamp",
  "completedAt": null,
  "retryCount": 1,
  "createdAt": "timestamp"
}
```

allowed currentStep:

timeline_analysis
clip_selection
transition
subtitle_burn
audio_sync
export

render progress는 realtime UI에서 사용한다.

## 상태 관리 구조

모든 pipeline 상태는 projects collection 기준으로 저장한다. renders collection은 render 세부 상태를 저장한다. frontend는 projects.status 기준으로 화면을 업데이트한다.

example:

```json id="k2s1"
{
  "status": "generating_images",
  "progress": 42
}
```

상태 변경 시 updatedAt 자동 갱신 필수.

## Firebase Storage 구조

모든 생성 asset은 Firebase Storage 저장을 기본 원칙으로 한다.

path:

/projects/{projectId}/lyrics/

/projects/{projectId}/audio/

/projects/{projectId}/images/

/projects/{projectId}/clips/

/projects/{projectId}/subtitle/

/projects/{projectId}/render/

example:

/projects/proj_001/audio/audio.mp3

/projects/proj_001/render/final.mp4

output rule:

lyrics.json
audio.mp3
subtitle.ass
preview.mp4
final.mp4
metadata.json

temp asset 저장 금지.

## Security Rule 원칙

모든 firestore document는 uid ownership 검증 필수다. 인증되지 않은 사용자는 접근 금지한다. 타 사용자 project 접근 금지한다.

rule:

user.uid == document.uid

example:

allowed:

내 uid 프로젝트 접근

denied:

다른 uid 프로젝트 접근

public access 금지.

## Query Rule

Frontend query는 최소화한다. 반드시 uid 기반 filtering 사용한다.

allowed:

projects where uid = current user

renders where uid = current user

금지:

전체 collection scan

unbounded query

offset pagination 남용

pagination은 cursor 기반 사용.

## Index Rule

Firestore composite index 사용을 허용한다.

recommended index:

uid + createdAt

uid + status

projectId + createdAt

renderId + projectId

최근 프로젝트 조회 성능 최적화 목적이다.

## Cache 및 Resume Rule

Firestore document는 pipeline resume source 역할을 수행한다. 실패 시 성공 단계 재생성 금지 원칙을 따른다.

예시:

lyrics success
music success
image success
video failed

retry:

video부터 재개

retryCount 증가 필수.

## 데이터베이스 원칙

Firestore는 상태와 metadata 저장소이며 Storage는 asset 저장소다. Firestore에 binary 저장 금지. schema breaking change 금지. nullable field 최소화. 모든 document는 deterministic contract를 유지해야 하며 “resume 가능한 stateful pipeline”을 최우선 원칙으로 한다.
