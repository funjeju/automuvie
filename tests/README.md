# tests

- Backend pipeline smoke test: `src/backend/tests/test_pipeline_smoke.py`
  - 실행: `cd src/backend && pytest -v`
  - mock provider 기반 — ffmpeg가 설치된 환경에서 실제 mp4까지 생성됩니다.

향후 추가:
- Render unit test (clip planner / transition graph)
- API e2e (httpx + asgi)
- Frontend Playwright
