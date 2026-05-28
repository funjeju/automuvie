좋습니다. `01-product-spec.md`를 실제 개발 착수 가능한 수준으로, 단락 최대한 붙여서 작성합니다.

# 01-product-spec.md

# Product Specification (PRD)

## 1. Objective

본 서비스는 사용자가 장르, 분위기, 프롬프트만 입력하면 AI가 자동으로 가사 생성 → 음악 생성 → 이미지 생성 → 영상 생성 → 자막 생성 → 최종 뮤직비디오(mp4) 출력까지 수행하는 AI 기반 자동 뮤직비디오 생성 플랫폼이다. 사용자는 전문 영상 편집 지식 없이 2~3분 수준의 감성적·시네마틱 뮤직비디오를 생성할 수 있어야 한다. 본 문서는 MVP 기준 제품 요구사항을 정의하며 개발자가 추가 질문 없이 기능 구현 가능한 수준을 목표로 한다.

## 2. Product Goal

핵심 목표는 “몇 번의 클릭만으로 완성도 높은 AI 뮤직비디오 생성”이다. 사용자는 prompt 입력 후 생성 버튼 클릭만으로 최종 mp4 다운로드까지 완료할 수 있어야 한다. 시스템은 생성 과정의 복잡함을 숨기고 자동 orchestration을 수행한다. 영상 생성 과정은 fully automated를 원칙으로 하며 사용자의 manual editing을 최소화한다.

## 3. Target User

주 사용자층은 AI 콘텐츠 제작 입문자, 유튜브 크리에이터, 감성 음악 영상 제작자, 쇼츠/뮤직비디오 제작자, 개인 브랜딩 사용자, 음악 생성 실험 사용자다. 전문 편집툴 경험이 없어도 사용할 수 있어야 하며 영상 편집보다 “결과물 생성 속도”를 우선한다.

## 4. MVP Scope

MVP는 최소 기능 중심으로 구성한다. 입력값은 genre, mood, free prompt, duration(60~180초)만 허용한다. 출력값은 lyrics.json, audio.mp3, generated images, generated clips, subtitle.ass, preview.mp4, final.mp4만 제공한다. MVP에서는 타임라인 수동편집, collaborative editing, social feed, community, template marketplace, mobile app, multi-project collaboration 기능은 제외한다.

## 5. User Flow

유저 플로우는 아래 순서를 반드시 따른다.

Landing → Prompt Input → Lyrics Generation → Music Generation → Image Generation → Video Generation → Rendering Progress → Preview → Download

사용자는 홈에서 장르, 분위기, 프롬프트, 영상 길이를 입력한다. 생성 버튼 클릭 시 project가 생성되며 백엔드 task queue가 시작된다. 시스템은 단계별 상태를 Firestore에 저장하며 사용자는 progress 화면에서 현재 상태를 실시간 확인할 수 있다. 모든 생성이 완료되면 preview 화면으로 이동하며 최종 다운로드가 가능하다.

## 6. Functional Requirement

### 6.1 Prompt Input

사용자는 아래 값을 입력할 수 있다.

* Genre (필수)
* Mood (필수)
* Prompt (선택)
* Duration (필수)

예시 입력:

```json
{
  "genre": "cinematic emotional",
  "mood": "nostalgic",
  "prompt": "lonely city night with warm memories",
  "duration": 120
}
```

입력 validation 규칙:

* genre required
* mood required
* duration min 60
* duration max 180
* prompt max 500 chars

validation 실패 시 사용자에게 즉시 에러 메시지 표시.

### 6.2 Lyrics Generation

시스템은 Claude API를 사용하여 가사를 생성한다. 가사는 반드시 [Verse], [Chorus], [Bridge] 구조를 포함해야 하며 section metadata를 반환해야 한다. 생성 결과는 Firestore와 Storage에 저장한다.

expected output:

```json
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

실패 시 retry 3회 수행 후 failed 상태 전환.

### 6.3 Music Generation

시스템은 Lyria 3 Pro API를 사용해 mp3를 생성한다. duration은 user input 기준으로 생성하며 metadata를 저장한다.

output:

```json
{
  "audioUrl": "/storage/audio/project123.mp3",
  "duration": 118.2
}
```

생성 실패 시 retry 가능해야 하며 성공한 단계는 재생성 금지한다.

### 6.4 Image Generation

GPT Image API를 사용한다. 각 lyric section 기준 3~4개 이미지 variation 생성. 스타일 consistency 유지 필수. 동일 프로젝트는 visual tone consistency를 유지해야 한다.

예:

verse1 → 4 images
chorus1 → 4 images

resolution 기본값:

1080x1920

### 6.5 Video Generation

Veo 3.1 API 사용. section별 8~15초 clip 생성. motion prompt는 section lyric 기반 자동 생성. clip 부족 시 repeat 허용. failed clip은 fallback image zoom motion 사용 가능.

output example:

```json
{
  "sectionId": "verse_1",
  "clips": [
    {
      "url": "/storage/clips/clip1.mp4",
      "duration": 8.4
    }
  ]
}
```

### 6.6 Subtitle Generation

Whisper API 기반 timestamp 추출. subtitle format은 ASS 고정. karaoke color transition mandatory. word level timestamp 사용.

output:

subtitle.ass

### 6.7 Rendering

ffmpeg-python 기반 single render pipeline 사용. transition, fade, subtitle burn, audio sync를 한번에 처리한다.

출력:

* preview.mp4
* final.mp4

기본 export:

* 1080x1920
* H264
* AAC
* mp4

## 7. Project Status Flow

모든 프로젝트는 아래 status를 가진다.

queued → generating_lyrics → generating_music → generating_images → generating_video → generating_subtitle → rendering → completed

실패 시:

failed

사용자 취소 시:

cancelled

status는 Firestore에서 실시간 observable 상태여야 한다.

## 8. Success Metric

MVP 성공 기준:

1. 사용자가 60~180초 음악 영상을 생성 가능해야 함.
2. prompt 입력부터 final.mp4 다운로드까지 완료 가능해야 함.
3. 평균 생성 성공률 90% 이상.
4. 실패 시 resume 가능해야 함.
5. 생성 진행률을 사용자에게 실시간 표시해야 함.

## 9. Non Functional Requirement

생성 과정은 async 기반이어야 하며 UI blocking 금지. API timeout 발생 시 retry 적용. 모든 heavy task는 backend에서 처리한다. frontend는 orchestration과 progress UI만 담당한다. API key 하드코딩 금지. 동일 입력에 대한 cache 고려. 모든 생성물은 storage 저장 및 재사용 가능해야 한다.
