"""
경량 in-process async queue.
production에서는 Cloud Tasks / Redis RQ / Celery 등으로 교체하되 동일 interface 유지한다.
"""

from __future__ import annotations
import asyncio
from typing import Awaitable, Callable
from ..core.logger import get_logger

log = get_logger("queue")


class AsyncTaskQueue:
    def __init__(self) -> None:
        self._queue: asyncio.Queue[Callable[[], Awaitable[None]]] = asyncio.Queue()
        self._worker_task: asyncio.Task | None = None
        self._running: bool = False

    async def start(self) -> None:
        if self._running:
            return
        self._running = True
        self._worker_task = asyncio.create_task(self._loop())
        log.info("task queue started")

    async def stop(self) -> None:
        self._running = False
        if self._worker_task:
            self._worker_task.cancel()

    async def _loop(self) -> None:
        while self._running:
            try:
                job = await self._queue.get()
                try:
                    await job()
                except Exception as e:
                    log.exception(f"job error: {e}")
                finally:
                    self._queue.task_done()
            except asyncio.CancelledError:
                break

    async def submit(self, job: Callable[[], Awaitable[None]]) -> None:
        await self._queue.put(job)


_queue_singleton: AsyncTaskQueue | None = None


def get_task_queue() -> AsyncTaskQueue:
    global _queue_singleton
    if _queue_singleton is None:
        _queue_singleton = AsyncTaskQueue()
    return _queue_singleton
