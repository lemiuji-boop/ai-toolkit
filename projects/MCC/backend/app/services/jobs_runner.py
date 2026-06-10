"""Асинхронные задания (TZ-FINAL FR-070/071): 202-паттерн, статусы, этапы.
Хранилище статусов внедряется (InMemoryJobStore сейчас; DB-store — тонкая замена
в T-04 по тому же протоколу). Совместимо с Celery позже без смены API."""
import asyncio
import traceback
import uuid
from collections.abc import Awaitable, Callable
from typing import Any, Protocol

Stage = Callable[[str], Awaitable[None]]  # колбэк этапа для SSE
JobFn = Callable[[Stage], Awaitable[dict[str, Any]]]


class JobStore(Protocol):
    async def create(self, job_id: str) -> None: ...
    async def set_status(self, job_id: str, status: str, *,
                         stage: str | None = None,
                         result: dict | None = None,
                         error: str | None = None) -> None: ...
    async def get(self, job_id: str) -> dict: ...


class InMemoryJobStore:
    def __init__(self) -> None:
        self._jobs: dict[str, dict] = {}
        self._events: dict[str, asyncio.Queue[str]] = {}

    async def create(self, job_id: str) -> None:
        self._jobs[job_id] = {"job_id": job_id, "status": "queued", "stage": None,
                              "result": None, "error": None}
        self._events[job_id] = asyncio.Queue()

    async def set_status(self, job_id: str, status: str, *, stage=None, result=None, error=None):
        j = self._jobs[job_id]
        j["status"] = status
        if stage is not None:
            j["stage"] = stage
            await self._events[job_id].put(stage)
        if result is not None:
            j["result"] = result
        if error is not None:
            j["error"] = error

    async def get(self, job_id: str) -> dict:
        return dict(self._jobs[job_id])

    async def next_event(self, job_id: str, timeout: float = 30.0) -> str:
        return await asyncio.wait_for(self._events[job_id].get(), timeout)


class JobRunner:
    def __init__(self, store: JobStore):
        self.store = store

    async def submit(self, fn: JobFn) -> str:
        """Возвращает job_id немедленно (для 202), исполняет в фоне."""
        job_id = str(uuid.uuid4())
        await self.store.create(job_id)

        async def _run() -> None:
            async def stage(name: str) -> None:
                await self.store.set_status(job_id, "running", stage=name)
            try:
                await self.store.set_status(job_id, "running", stage="start")
                result = await fn(stage)
                await self.store.set_status(job_id, "done", stage="done", result=result)
            except Exception as e:  # ошибка задания — статус, не падение процесса
                await self.store.set_status(
                    job_id, "error",
                    error=f"{type(e).__name__}: {e}\n{traceback.format_exc(limit=3)}",
                )
        asyncio.create_task(_run())
        return job_id
