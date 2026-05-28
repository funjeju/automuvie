좋습니다. 디자인 md는 **3번째 파일(`03-frontend-ui-ux-design.md`)**입니다. 첨부 이미지를 기준으로, 최대한 단락 붙이고 소제목+서술형 중심으로 작성합니다. 단순 “예쁘게 만들기”가 아니라 **개발자가 그대로 구현 가능한 UI 스펙 문서** 기준입니다.

# 03-frontend-ui-ux-design.md

# Frontend UI/UX Design Specification

## 1. 디자인 목표

본 서비스 UI는 “AI 기반 시네마틱 뮤직비디오 제작 스튜디오” 느낌을 기본 컨셉으로 한다. 사용자가 전문 편집툴을 쓰는 느낌이 아니라 “감성적인 AI 창작 공간”에 들어온 경험을 받아야 한다. 디자인 방향은 cinematic, modern, premium, dark-first, neon accent를 기준으로 한다. 전체 UI는 생성형 AI 툴 특유의 미래적인 분위기를 유지하되 과도하게 복잡한 편집툴 느낌은 제거한다. 사용자는 복잡한 타임라인 편집이 아니라 “생성 → 확인 → 수정 → 다운로드” 흐름을 직관적으로 이해해야 한다.

## 2. 레이아웃 구조

전체 화면은 5영역 구조를 따른다. 좌측 Sidebar Navigation, 상단 Workflow Navigation, 중앙 Main Preview Workspace, 우측 Asset Panel, 하단 Timeline Workspace 구조를 기본으로 한다. Desktop 기준 1920px 최적화이며 최소 1440px 이상에서 안정적으로 동작해야 한다. Tablet에서는 우측 panel collapse 허용, 모바일에서는 timeline을 하단 drawer 방식으로 변경한다.

레이아웃 구조:

Left Sidebar → Top Workflow → Main Canvas + Right Panel → Bottom Timeline

모든 페이지는 동일 레이아웃 시스템을 유지하여 사용자가 화면 이동 시 학습 비용 없이 사용 가능해야 한다.

## 3. 디자인 톤앤매너

배경은 dark navy + purple gradient 기반을 사용한다. primary accent는 violet/neon purple 계열을 사용한다. 버튼 hover, progress, selected state는 glow 효과를 적용한다. flat design보다 glassmorphism을 일부 섞은 cinematic dashboard 스타일을 지향한다. border radius는 14~20px 기준으로 통일한다. shadow는 과하지 않게 soft neon shadow를 사용한다.

디자인 키워드:

* cinematic
* premium
* dark-first
* futuristic
* neon minimal
* creator studio

## 4. 컬러 시스템

Primary Color는 violet gradient 계열을 사용한다. Background는 deep navy 계열을 사용한다. card는 background 대비 8~12% 밝게 유지한다.

예시 기준:

Background:
#090B1A

Card:
#11142B

Primary:
#B14CFF

Primary Gradient:
#8A4DFF → #D946EF

Border:
rgba(255,255,255,0.08)

Text Primary:
#FFFFFF

Text Secondary:
rgba(255,255,255,0.7)

Success:
#4ADE80

Error:
#FF5C7A

Warning:
#FFC857

selected 상태는 neon border + subtle glow 조합으로 표현한다.

## 5. Typography

폰트는 modern sans-serif 계열 사용. Desktop은 Pretendard 우선 적용. fallback은 Inter 사용. 제목은 bold 계열 사용, body는 regular 중심으로 구성한다.

Typography rule:

Page Title:
28~32px

Section Title:
18~22px

Card Title:
14~16px

Body:
13~15px

Caption:
11~12px

모든 텍스트는 높은 대비 유지. dark UI에서 gray 텍스트 남용 금지.

## 6. Sidebar Navigation

좌측 sidebar는 프로젝트 전체 navigation 역할을 수행한다. width는 84~100px 고정. 메뉴는 vertical icon + label 구조를 사용한다.

메뉴:

* Project
* Album/Template
* Media
* Music
* Settings

selected 메뉴는 glow background를 적용한다. hover 시 subtle animation 제공. sidebar는 collapse 가능해야 한다.

상단에는 logo 영역을 둔다.

예시:

Vibe Creator

하단에는 settings shortcut 배치.

## 7. Top Workflow Navigation

상단 navigation은 생성 흐름(progress stepper) 역할을 수행한다.

순서:

Lyrics Generation → Music Generation → Image Generation → Video Generation → Subtitle → Render

현재 단계는 glow highlight 표시. 완료 단계는 success icon 처리. pending 상태는 dim 처리.

state:

inactive
active
completed
failed

상태 변화는 애니메이션으로 연결한다.

## 8. Main Preview Workspace

중앙 preview는 가장 큰 비중을 가진다. 사용자가 현재 생성 중인 결과를 확인하는 영역이다. preview는 16:9 또는 9:16 비율을 지원하되 기본은 vertical shortform(1080x1920) 기준으로 한다.

구성:

* lyric section list
* preview player
* playback control
* progress bar
* duration indicator

lyric section panel은 좌측에 위치하며 Verse, Chorus, Bridge 구간을 보여준다. 현재 재생 중인 구간 highlight 적용. section click 시 preview seek 이동.

player controls:

* play
* pause
* next
* previous
* timeline drag

## 9. Asset Panel

우측 panel은 생성 asset 관리 영역이다. 생성된 이미지, clip variation, alternative assets를 표시한다. 기본은 image gallery 구조를 사용한다.

구성:

* image tab
* video tab
* variation selector

이미지는 2~3열 grid 사용. selected asset은 border glow 적용. “+ 더 생성” 버튼 제공.

state:

loading
completed
failed
retrying

loading 시 skeleton UI 사용.

## 10. Timeline Workspace

하단 timeline은 최종 composition preview 역할을 수행한다. 전문 편집툴 수준 편집은 제공하지 않으며 lightweight timeline 구조를 유지한다.

구성:

* clip strip
* audio waveform
* lyric timing
* active section indicator

timeline card는 section 단위 구성.

예시:

Verse1
Chorus1
Verse2
Bridge
Chorus2

drag reorder는 MVP 제외. 클릭 시 preview 이동만 지원.

## 11. Button System

버튼은 Primary / Secondary / Ghost 세 종류를 사용한다.

Primary:
gradient fill

Secondary:
outline

Ghost:
transparent

주요 CTA:

* Generate
* Retry
* Preview
* Export MP4

hover 시 subtle glow animation 적용.

## 12. Loading UX

AI 생성 시간이 길기 때문에 loading UX는 매우 중요하다. spinner 사용 최소화. skeleton + progress message 기반 사용.

예:

“Lyrics generating...”
“Creating cinematic visuals...”
“Rendering final music video...”

예상 시간 표시 optional.

## 13. Error UX

에러 발생 시 사용자에게 technical error 노출 금지.

예:

Bad:
API timeout error

Good:
“영상 생성 중 문제가 발생했습니다. 다시 시도해주세요.”

retry button 필수 제공.

## 14. Responsive Rule

Desktop first 기준으로 설계한다.

Desktop:
full layout

Tablet:
right panel collapse

Mobile:
timeline bottom drawer
sidebar icon-only mode

horizontal scroll 최소화.

## 15. UX Principle

UI 목표는 “복잡한 편집툴”이 아니라 “AI 창작 도우미”다. 사용자는 항상 현재 생성 단계, 진행률, 예상 결과를 직관적으로 이해해야 한다. 불필요한 클릭을 줄이고 preview 중심 UX를 유지한다. 디자인 우선순위는 clarity > emotion > complexity 순서를 따른다.
