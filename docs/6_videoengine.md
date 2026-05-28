좋습니다. 6번은 **`06-video-rendering-engine.md`** 입니다. 이 문서는 ffmpeg-python 기반 최종 영상 합성 엔진 규격서입니다. 개발자가 그대로 구현할 수 있도록 **렌더 순서, clip repeat, transition, subtitle burn, codec, bitrate, fallback**까지 정의합니다.

# 06-video-rendering-engine.md

# Video Rendering Engine

## 렌더링 엔진 개요

본 문서는 최종 mp4 생성 엔진 규격을 정의한다. 모든 영상 렌더링은 ffmpeg-python 기반 single pipeline 방식으로 처리한다. shell 기반 ffmpeg string 난립을 금지하며 ffmpeg-python graph chaining 방식만 허용한다. 렌더링 엔진은 AI가 생성한 image, video clip, subtitle, audio asset을 timeline 기준으로 자동 합성한다. 사용자의 수동 편집 없이 최종 cinematic music video를 생성하는 것이 목적이다.

render pipeline:

Audio Analysis → Timeline Allocation → Clip Selection → Clip Repeat → Transition → Subtitle Burn → Audio Sync → Final Export

모든 rendering은 backend worker에서 async 처리한다. frontend rendering 금지.

## 입력 데이터 구조

렌더링 엔진은 project 단위로 동작한다. pipeline 실행 전 모든 asset이 준비되어 있어야 한다.

필수 입력:

* audio.mp3
* timeline.json
* generated clips
* generated images
* subtitle.ass

input example:

```json id="d1f9"
{
  "projectId": "proj_001",
  "audioUrl": "audio.mp3",
  "subtitleUrl": "subtitle.ass",
  "timeline": [
    {
      "sectionId": "verse_1",
      "start": 0,
      "end": 21.5
    }
  ]
}
```

입력 validation 실패 시 rendering 시작 금지.

필수 조건:

* audio required
* subtitle required
* minimum one visual asset required

## 오디오 길이 분석

렌더링 시작 전 pydub을 사용하여 실제 mp3 duration을 분석한다. user requested duration을 신뢰하지 않고 실제 audio duration 기준으로 timeline을 계산한다. 모든 영상 길이는 audio length에 정확히 sync되어야 한다.

rule:

* audio length source of truth
* audio sync priority
* video length must equal audio length

example:

audio duration:

118.2 sec

final render duration:

118.2 sec

오차 허용:

±0.2초

## Timeline 배치 규칙

timeline은 lyric section 기준으로 생성한다. section start/end time 기준 clip을 자동 배치한다. clip 부족 시 repeat 허용한다. section 간 abrupt cut을 최소화하고 cinematic continuity를 유지해야 한다.

example:

Verse1 → 0~22 sec
Chorus1 → 22~41 sec
Verse2 → 41~63 sec

각 section은 독립 timeline unit으로 처리한다.

## Clip 선택 규칙

각 lyric section은 생성된 clips 중 자동 선택된다. 기본 random weighted selection을 사용하되 visual continuity 우선 정책을 적용한다.

rule:

* section clip priority
* duplicate clip 최소화
* motion continuity 유지
* abrupt camera change 최소화

예시:

verse_1:

clip1.mp4
clip2.mp4
clip3.mp4

timeline duration이 길 경우 repeat 사용 가능.

## Clip Repeat 규칙

AI clip 길이가 부족할 경우 repeat 허용한다. 단순 loop보다 cinematic repeat를 우선 적용한다.

allowed repeat:

* reverse repeat
* zoom crop variation
* speed adjustment
* alternate clip reuse

bad:

A A A A A 반복

good:

A → B → A zoom → C → B crop

반복 시 시청 피로도를 최소화해야 한다.

## Image Fallback 규칙

video generation 실패 시 image motion rendering을 fallback으로 사용한다. 정적 이미지 사용 금지. 모든 이미지는 motion effect 적용 필수.

allowed motion:

* slow zoom in
* slow zoom out
* pan left
* pan right
* cinematic parallax

image clip duration:

4~8초

image fallback은 Ken Burns style animation 기반으로 구현한다.

## Transition 규칙

모든 clip 연결 시 cinematic transition을 적용한다. hard cut 남용 금지. 기본 transition은 cross dissolve 기반으로 한다.

allowed transition:

* fade in
* fade out
* cross dissolve
* soft blur transition

transition duration:

0.4~1.2 sec

rule:

verse → chorus 전환은 stronger transition 허용.

## Subtitle Burn 규칙

subtitle은 ASS karaoke subtitle을 사용한다. soft subtitle 금지. 반드시 burn-in subtitle 사용한다. lyric sync를 최우선으로 유지한다.

subtitle rule:

* word sync mandatory
* karaoke color transition mandatory
* center aligned
* mobile readability priority

style:

* glow effect
* shadow
* large readable font

subtitle safe zone 유지.

## Audio Sync 규칙

audio는 source of truth다. video는 반드시 audio duration에 맞춰 조정한다. mismatch 허용 금지.

rule:

* no audio trimming
* no subtitle desync
* video auto trim allowed

priority:

audio > subtitle > video

## Export 규칙

모든 export는 vertical shortform 기준으로 수행한다.

default export:

resolution:

1080x1920

fps:

30fps

codec:

H264

audio codec:

AAC

container:

MP4

bitrate:

video: 8Mbps
audio: 320kbps

preview export:

720x1280

final export:

1080x1920

## Storage 구조

렌더 결과물은 Firebase Storage 저장을 기본으로 한다.

storage:

/projects/{projectId}/render/

output:

preview.mp4
final.mp4
metadata.json

metadata example:

```json id="v3k1"
{
  "duration": 118.2,
  "resolution": "1080x1920",
  "fps": 30
}
```

## Render Status Rule

render status는 Firestore에 기록한다.

flow:

rendering → completed

실패 시:

failed

progress example:

```json id="j2s1"
{
  "status": "rendering",
  "progress": 78,
  "currentStep": "subtitle_burn"
}
```

frontend는 progress realtime 표시를 지원해야 한다.

## Retry 및 Resume 규칙

rendering 실패 시 max retry 3회를 적용한다. 이미 성공한 asset generation은 재실행 금지한다. render restart는 rendering 단계부터 resume 수행한다.

example:

lyrics success
music success
video success
render failed

retry:

render only restart

## 렌더링 엔진 원칙

본 엔진은 “자동 cinematic music video generator”를 목표로 한다. 복잡한 편집 기능보다 visual continuity, subtitle sync, audio consistency를 우선한다. 모든 rendering은 deterministic contract 기반으로 구현하며 shell ffmpeg command hardcoding 금지, ffmpeg-python graph 기반 구현을 강제한다.
