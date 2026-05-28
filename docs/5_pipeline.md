좋습니다. 5번은 **`05-ai-generation-pipeline.md`** 입니다. 이 문서는 이 서비스의 핵심 엔진 문서입니다. Claude → Lyria → GPT Image → Veo → Whisper → Render까지의 생성 흐름, retry, fallback, cache, contract를 정의합니다. 스타일은 앞과 동일하게 **소제목 + 서술형**, 단락 붙여서 갑니다.

# 05-ai-generation-pipeline.md

# AI Generation Pipeline

## 생성 파이프라인 개요

본 시스템의 핵심은 AI generation pipeline이다. 사용자가 genre, mood, prompt, duration을 입력하면 backend worker는 정해진 순서대로 AI 생성 작업을 수행한다. 모든 단계는 stateful 해야 하며 실패 시 resume 가능해야 한다. 성공한 단계는 절대 재생성하지 않는다. pipeline은 반드시 lyrics → music → image → video → subtitle → render 순서를 따른다. 단계 skip 금지 원칙을 적용한다.

Pipeline Flow:

Prompt Input → Claude Lyrics → Lyria Music → GPT Image → Veo Video → Whisper Subtitle Timestamp → ffmpeg Rendering → Final MP4

모든 단계는 Firebase Storage 저장을 기본 원칙으로 하며 Firestore status를 실시간 갱신한다.

## 입력 데이터 규칙

모든 생성 파이프라인은 동일한 입력 contract를 사용한다. backend worker는 아래 project payload를 기준으로 pipeline을 실행한다.

input:

```json id="g31a"
{
  "projectId": "proj_001",
  "genre": "cinematic emotional",
  "mood": "nostalgic",
  "prompt": "warm memories in lonely city",
  "duration": 120
}
```

validation rule:

* genre required
* mood required
* duration min 60
* duration max 180
* prompt optional
* projectId required

입력 validation 실패 시 pipeline 실행 금지.

## Claude Lyrics Generation

첫 단계는 lyrics generation이다. Claude API를 사용한다. 가사는 반드시 section 구조를 가져야 하며 [Verse], [Chorus], [Bridge] 포맷을 포함한다. duration 기준으로 lyric length를 자동 조절해야 한다. tone은 genre + mood + prompt 조합 기반으로 생성한다.

생성 규칙:

* Verse mandatory
* Chorus mandatory
* Bridge optional
* section metadata required
* section ordering required

예시:

60초 → Verse1 / Chorus1 / Verse2 / Chorus2

120초 → Verse1 / Chorus1 / Verse2 / Chorus2 / Bridge / Chorus3

180초 → Verse1 / Chorus1 / Verse2 / Chorus2 / Bridge / Verse3 / Chorus3

output:

```json id="h29c"
{
  "sections": [
    {
      "sectionId": "verse_1",
      "type": "verse",
      "order": 1,
      "text": "city lights falling softly"
    },
    {
      "sectionId": "chorus_1",
      "type": "chorus",
      "order": 2,
      "text": "stay with me tonight"
    }
  ]
}
```

실패 시 retry 최대 3회 수행. 성공 결과는 lyrics.json 저장.

storage:

/projects/{projectId}/lyrics/lyrics.json

## Lyria Music Generation

lyrics 생성 완료 후 Lyria 3 Pro API를 사용해 mp3를 생성한다. 입력값은 genre, mood, lyrics structure, duration이다. 음악은 duration 기준 ±5초 오차 허용한다. backend는 최종 길이를 metadata에 기록해야 한다.

output:

```json id="v81b"
{
  "audioUrl": "audio.mp3",
  "duration": 118.2,
  "sampleRate": 44100
}
```

storage:

/projects/{projectId}/audio/audio.mp3

성공 이후 동일 project 재생성 금지.

## GPT Image Generation

lyrics section 기준 이미지를 생성한다. section마다 기본 4개 variation을 생성한다. visual consistency를 유지해야 하므로 동일 project에서는 style continuity 유지 규칙을 적용한다. section lyric 기반 prompt를 자동 생성하며 genre, mood를 prompt modifier로 사용한다.

규칙:

* section당 4 image
* vertical ratio
* cinematic style
* same mood continuity
* same color tone continuity

example:

verse_1 → 4 images
chorus_1 → 4 images

output:

```json id="n92p"
{
  "sectionId": "verse_1",
  "images": [
    "image1.png",
    "image2.png",
    "image3.png",
    "image4.png"
  ]
}
```

storage:

/projects/{projectId}/images/

실패 시 retry 수행. 이미지 실패 시 placeholder 사용 금지.

## Veo Video Generation

image generation 완료 후 Veo 3.1 API를 사용하여 영상 clip을 생성한다. lyric section 단위 생성 원칙을 따른다. clip 길이는 기본 8~15초다. motion prompt는 lyric semantic 기반 자동 생성한다.

규칙:

* 9:16 vertical
* cinematic motion
* 8~15 sec clip
* section-based generation
* smooth motion priority

example:

verse_1 → clip 3개 생성
chorus_1 → clip 4개 생성

output:

```json id="u12q"
{
  "sectionId": "verse_1",
  "clips": [
    {
      "url": "clip1.mp4",
      "duration": 9.2
    },
    {
      "url": "clip2.mp4",
      "duration": 10.4
    }
  ]
}
```

storage:

/projects/{projectId}/clips/

video generation 실패 시 fallback image motion 사용 가능하다. image zoom, slow pan, cinematic movement를 적용한다.

## Audio Timeline Analysis

music 생성 완료 후 pydub 기반 duration 분석을 수행한다. 실제 audio length를 계산하고 section별 timing을 자동 배분한다. lyric section order 기준으로 timeline을 생성한다.

output example:

```json id="f19w"
{
  "timeline": [
    {
      "sectionId": "verse_1",
      "start": 0,
      "end": 22.4
    }
  ]
}
```

storage:

/projects/{projectId}/timeline/

## Whisper Subtitle Timestamp Extraction

Whisper API를 사용하여 lyric alignment를 수행한다. 반드시 word-level timestamp를 사용한다. subtitle format은 ASS 기반 karaoke subtitle로 생성한다.

rule:

* word timestamp mandatory
* karaoke highlight mandatory
* lyric sync priority

output:

subtitle.ass

storage:

/projects/{projectId}/subtitle/

## Cache Rule

비용 절감을 위해 cache 사용을 허용한다. 동일 입력은 cached result 우선 사용한다.

cache key:

genre + mood + prompt + duration + seed

cache 대상:

* lyrics
* music
* image
* video

subtitle과 render는 cache 제외.

## Retry Rule

모든 단계는 retry 가능해야 한다. retry max count는 3회다. exponential backoff 적용한다.

예시:

attempt1 → fail
attempt2 → fail
attempt3 → fail

→ failed status

## Resume Rule

pipeline은 반드시 resume 가능해야 한다. 성공한 단계는 재생성 금지.

예시:

lyrics success
music success
image success
video failed

resume 시:

video generation부터 시작

music 재생성 금지.

## Status Update Rule

각 단계 종료 시 Firestore 상태를 갱신한다.

state flow:

queued → generating_lyrics → generating_music → generating_images → generating_video → generating_subtitle → rendering → completed

실패 시:

failed

사용자 취소 시:

cancelled

frontend는 realtime status 기준으로 UI를 갱신한다.

## Pipeline 원칙

본 시스템은 fully automated AI generation을 원칙으로 한다. 사용자 manual editing 최소화, visual consistency 유지, resume 가능성 보장, stateful generation, 비용 최적화를 핵심 목표로 한다. 모든 생성 단계는 deterministic contract 기반으로 구현되어야 하며 “성공한 단계 재생성 금지” 원칙을 반드시 따른다.
