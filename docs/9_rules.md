좋습니다. 마지막 9번은 **`09-development-rules.md`** 입니다. 이 문서는 팀 전체 코드 품질과 구조를 강제하는 규칙 문서입니다. Cursor, Claude Code, Copilot, 사람 개발자까지 모두 같은 규칙으로 움직이게 만드는 목적입니다.

# 09-development-rules.md

# Development Rules

## 개발 원칙

본 프로젝트는 “빠르게 만드는 코드”보다 “유지보수 가능한 코드”를 우선한다. 모든 개발자는 동일한 architecture rule, naming convention, folder convention, typing policy를 따라야 한다. frontend와 backend 모두 deterministic structure를 유지해야 하며 AI coding assistant(Cursor, Claude, ChatGPT, Copilot)가 생성한 코드도 본 문서 규칙을 반드시 준수해야 한다. 구현 속도를 이유로 hardcoding, duplicated logic, business logic leakage를 허용하지 않는다.

핵심 원칙:

* readable code
* reusable code
* deterministic architecture
* strict typing
* low coupling
* high maintainability

## 폴더 구조 규칙

프로젝트 구조는 frontend와 backend를 분리한다. 기능(feature)보다 책임(responsibility) 기준 구조를 우선한다.

structure:

```txt id="a1b2"
project-root/
│
├── core.md
├── docs/
│
├── frontend/
│   ├── app/
│   ├── components/
│   ├── services/
│   ├── hooks/
│   ├── lib/
│   ├── types/
│   ├── store/
│   ├── constants/
│   └── utils/
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── services/
│   │   ├── repositories/
│   │   ├── models/
│   │   ├── dto/
│   │   ├── workers/
│   │   ├── render/
│   │   ├── config/
│   │   └── utils/
│
├── temp/
├── tests/
└── scripts/
```

rule:

* folder responsibility clear
* utils dumping 금지
* shared logic duplication 금지

## TypeScript 규칙

Frontend는 TypeScript strict mode를 강제한다. any 사용 금지 원칙을 적용한다. interface 또는 type 정의를 반드시 사용해야 한다.

required:

```txt id="b2c3"
"strict": true
```

금지:

```ts id="c3d4"
const data: any
```

허용:

```ts id="d4e5"
type ProjectStatus =
  | "queued"
  | "generating_music"
  | "completed"
```

rule:

* explicit typing mandatory
* inferred type 과신 금지
* reusable type 분리

## Python 규칙

Backend는 Python 3.12+ 기준으로 작성한다. typing mandatory, async-first 원칙을 따른다. sync blocking call 남용 금지.

bad:

```python id="e5f6"
def generate():
    pass
```

good:

```python id="f6g7"
async def generate_music(
    project_id: str
) -> MusicResult:
    pass
```

rule:

* typing required
* async required
* service layer mandatory
* repository pattern mandatory

## Architecture 규칙

Frontend business logic 금지 원칙을 적용한다. backend는 layered architecture를 따른다.

architecture:

Controller(API) → Service → Repository → Database

설명:

Controller는 request validation만 담당한다. Service는 business logic 수행한다. Repository는 DB access만 수행한다.

bad:

controller에서 Firestore query 실행

good:

controller → service → repository

## DTO 규칙

API request/response는 DTO(Data Transfer Object)를 사용한다. raw dict 반환 금지 원칙을 적용한다.

bad:

```python id="g7h8"
return {
    "status": "ok"
}
```

good:

```python id="h8i9"
return ProjectResponseDTO(
    status="ok"
)
```

rule:

* request dto
* response dto
* validation dto

mandatory.

## Naming Convention

모든 naming은 명확성과 예측 가능성을 우선한다.

Frontend:

component:

PascalCase

예:

GenerateButton.tsx

hook:

camelCase + use prefix

예:

useProjectStatus.ts

constant:

UPPER_CASE

예:

MAX_RETRY_COUNT

Backend:

file:

snake_case

예:

music_generation_service.py

class:

PascalCase

예:

RenderService

function:

snake_case

예:

generate_subtitle()

database field:

camelCase

예:

createdAt

금지:

```txt id="i9j0"
tmpData
test123
abc
foo
bar
```

## API 규칙

API endpoint는 REST convention을 따른다. verb duplication 금지한다.

bad:

```txt id="j1k2"
/createProject
/getProject
```

good:

```txt id="k2l3"
/project/create
/project/{id}
```

response format은 반드시 통일한다.

example:

```json id="l3m4"
{
  "success": true,
  "data": {},
  "message": "ok"
}
```

## Error Handling 규칙

try/catch 무시 금지. swallow error 금지. 모든 에러는 structured logging 해야 한다.

bad:

```python id="m4n5"
try:
    run()
except:
    pass
```

good:

```python id="n5o6"
try:
    run()
except Exception as e:
    logger.error(e)
    raise
```

rule:

* fail silently 금지
* retry awareness
* error code mandatory

## State Management 규칙

Frontend state는 최소화한다. server state 우선 원칙을 적용한다. project progress는 Firestore realtime 또는 API polling 기준으로 관리한다.

rule:

* local duplicated state 금지
* backend source of truth 유지
* optimistic update 최소화

## Testing 규칙

핵심 business logic 테스트 mandatory. render, pipeline, repository layer 테스트 작성해야 한다.

required test:

* pipeline test
* render test
* api test
* repository test
* retry test

coverage target:

minimum 80%

test naming:

```txt id="o6p7"
test_generate_music_success
test_render_retry
```

## Git Convention

branch naming 규칙을 강제한다.

branch:

feature/*
fix/*
refactor/*
hotfix/*

example:

```txt id="p7q8"
feature/render-engine
fix/subtitle-sync
```

commit convention:

feat:
fix:
refactor:
docs:
test:

example:

```txt id="q8r9"
feat: implement render pipeline
fix: subtitle sync bug
docs: update api spec
```

## 금지사항

다음 항목은 절대 금지한다.

* hardcoding
* duplicated logic
* frontend business logic
* blocking api call
* any overuse
* silent exception
* ffmpeg shell command hardcoding
* temp file accumulation
* magic number 남용
* direct firestore query inside component

bad:

```ts id="r9s0"
if(status === 7)
```

good:

```ts id="s0t1"
if(status === PROJECT_STATUS.RENDERING)
```

## 코드 리뷰 규칙

모든 PR은 architecture violation 검토를 우선한다. “작동한다”보다 “구조가 맞는가”를 먼저 본다.

review checklist:

* typing correct
* duplication 없음
* service layer 준수
* dto 사용
* error handling 있음
* logging 있음
* retry 고려됨
* test 작성됨

## 개발 원칙

본 프로젝트는 AI assisted development를 적극 허용한다. 단, AI가 생성한 코드도 본 문서 규칙을 위반하면 폐기한다. 코드 품질 기준은 사람과 동일하다. 구현 속도보다 유지보수성, deterministic architecture, resume 가능한 pipeline 안정성을 우선한다. “대충 동작하는 코드”보다 “예측 가능한 코드”를 목표로 한다.
