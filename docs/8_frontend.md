좋습니다. 8번은 **`08-deployment-vercel-firebase.md`** 입니다. 이 문서는 “신입 개발자도 배포 가능” 수준으로, Vercel + Firebase + FastAPI backend 운영 규칙, env, CI/CD, logging, monitoring까지 정의합니다. 스타일 동일하게 **소제목 + 서술형**, 단락 최대한 붙여서 갑니다.

# 08-deployment-vercel-firebase.md

# Deployment Vercel + Firebase

## 배포 구조

본 서비스는 Vercel + Firebase + FastAPI 구조를 사용한다. Frontend는 Vercel에 배포하고 Backend(FastAPI)는 container 기반 서버에 배포한다. Firebase는 Authentication, Firestore, Storage를 담당한다. Vercel은 frontend hosting 역할만 수행하며 heavy processing를 처리하지 않는다. 모든 AI generation, ffmpeg rendering, subtitle generation은 backend worker에서 수행한다.

architecture:

Next.js (Vercel) → FastAPI Server → Firebase → AI APIs → Render Worker

Frontend와 Backend는 완전히 분리된 deployment 구조를 사용한다. backend는 ffmpeg, pydub, whisper dependency를 안정적으로 실행할 수 있는 환경이어야 한다.

## 환경 분리 정책

배포 환경은 local, development, staging, production 4단계로 구분한다. 환경별 env를 분리하며 key 공유 금지 원칙을 적용한다.

environment:

local
development
staging
production

rule:

* production key local 사용 금지
* staging DB production 연결 금지
* env hardcoding 금지
* API key git commit 금지

## Frontend 배포

Frontend는 Next.js App Router 기반이며 Vercel deployment를 사용한다. main branch merge 시 자동 배포를 허용한다. preview deployment를 기본 활성화한다.

deployment flow:

GitHub Push → Vercel Build → Preview Deploy → Production Deploy

build command:

```txt id="q1w2"
npm run build
```

output directory:

```txt id="o9d1"
.next
```

Node version:

```txt id="e1p2"
>=20
```

frontend env example:

```env id="m1n2"
NEXT_PUBLIC_API_BASE_URL=https://api.domain.com
NEXT_PUBLIC_FIREBASE_API_KEY=xxxx
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=xxxx
NEXT_PUBLIC_FIREBASE_PROJECT_ID=xxxx
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=xxxx
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=xxxx
NEXT_PUBLIC_FIREBASE_APP_ID=xxxx
```

rule:

NEXT_PUBLIC prefix 없는 env를 frontend에서 사용 금지.

## Backend 배포

Backend는 FastAPI 기반이며 container deployment를 기본으로 한다. Vercel serverless backend 금지 원칙을 적용한다. 이유는 ffmpeg, render processing, long-running task, file system dependency 때문이다.

required dependency:

* ffmpeg
* python 3.12+
* pydub
* fastapi
* firebase-admin
* whisper api client
* storage sdk

backend 실행:

```txt id="c8m2"
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

backend env example:

```env id="z7s1"
ENV=production
API_BASE_URL=https://api.domain.com
FIREBASE_PROJECT_ID=xxxx
FIREBASE_PRIVATE_KEY=xxxx
FIREBASE_CLIENT_EMAIL=xxxx
CLAUDE_API_KEY=xxxx
LYRIA_API_KEY=xxxx
OPENAI_API_KEY=xxxx
VEO_API_KEY=xxxx
WHISPER_API_KEY=xxxx
JWT_SECRET=xxxx
```

rule:

backend env frontend 노출 금지.

## Firebase 설정

Firebase는 Auth, Firestore, Storage 사용을 기본으로 한다. anonymous auth 금지. authenticated user only 원칙을 적용한다.

enable service:

* Authentication
* Firestore Database
* Storage

disable:

* anonymous auth
* public storage

Firestore mode:

production mode

Storage mode:

authenticated only

## Firebase Authentication

로그인은 Firebase Auth 사용을 기본으로 한다. JWT 기반 인증을 사용한다. frontend는 Firebase token을 backend Authorization header에 포함해야 한다.

example:

```txt id="r9u2"
Authorization: Bearer firebase_token
```

rule:

backend에서 token verification mandatory.

## Firestore 배포 규칙

Firestore schema 변경 시 migration 문서를 반드시 작성한다. breaking schema change 금지 원칙을 적용한다.

rule:

* nullable 최소화
* deterministic schema 유지
* uid ownership 유지
* composite index 사용

recommended index:

uid + createdAt

uid + status

projectId + createdAt

## Storage 배포 규칙

Storage는 generated asset 저장 전용이다. temp asset permanent upload 금지 원칙을 적용한다.

structure:

/projects/{projectId}/audio/

/projects/{projectId}/images/

/projects/{projectId}/clips/

/projects/{projectId}/subtitle/

/projects/{projectId}/render/

cleanup:

local temp file auto delete mandatory.

## Domain 구조

서비스는 frontend domain과 backend domain 분리를 권장한다.

example:

frontend:

app.domain.com

backend:

api.domain.com

storage:

Firebase Storage CDN

rule:

backend direct IP 사용 금지.

## CI/CD 정책

GitHub Actions 기반 CI/CD를 기본 권장한다. pull request merge 전 build validation mandatory.

pipeline:

lint → typecheck → build → test → deploy

example:

```txt id="j3n1"
npm run lint
npm run type-check
npm run build
pytest
```

production deploy는 main branch 기준으로 수행한다.

## Logging 정책

모든 generation step은 structured logging을 사용한다. print debugging 금지.

required log:

* request id
* project id
* user id
* current step
* error code
* latency

example:

```json id="t7m2"
{
  "projectId": "proj_001",
  "step": "generating_video",
  "latency": 12432
}
```

rule:

sensitive data logging 금지.

금지:

* API key log
* token log
* private prompt log

## Monitoring 정책

서비스 운영 시 monitoring mandatory. generation success rate, render failure rate, API latency, storage usage 추적 필수.

track metric:

* render success rate
* subtitle sync failure
* generation latency
* retry count
* queue waiting time
* completed project count

critical alert:

render failure > 15%

queue stuck > 5 min

API timeout spike

## Backup 정책

Firestore export backup 수행 권장. daily backup 기준 운영한다. storage backup lifecycle rule 적용한다.

rule:

daily backup

7 day retention

production restore test monthly

## Secret 관리 정책

모든 secret은 env 기반 관리한다. Git commit 금지. plaintext config 저장 금지.

bad:

```txt id="u1v2"
const API_KEY = "abc123"
```

good:

```txt id="x8z2"
process.env.CLAUDE_API_KEY
```

secret rotation 주기 운영 권장.

## 장애 대응 정책

backend failure 시 retry queue를 사용한다. rendering 중단 시 render step부터 resume 수행한다. frontend는 graceful fallback UI를 제공해야 한다.

example:

video success
subtitle success
render fail

retry:

render restart only

## 배포 원칙

본 서비스는 “Frontend Lightweight + Backend Heavy” 원칙을 따른다. frontend는 빠른 배포와 UI 제공 역할만 담당하며 backend는 AI generation과 rendering을 담당한다. production 안정성을 우선하며 serverless long-running rendering 금지, env 분리, structured logging, monitoring, resume 가능성을 핵심 운영 원칙으로 한다.
