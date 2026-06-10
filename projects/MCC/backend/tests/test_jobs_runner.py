import asyncio
import pytest
from app.services.jobs_runner import InMemoryJobStore, JobRunner


@pytest.mark.asyncio
async def test_lifecycle_done_with_stages():
    store = InMemoryJobStore()
    runner = JobRunner(store)

    async def work(stage):
        await stage("распознавание")
        await stage("геометрия")
        await stage("расчёт")
        return {"rows": 1}

    job_id = await runner.submit(work)            # немедленный возврат (202)
    assert (await store.get(job_id))["status"] in ("queued", "running")
    for _ in range(50):
        if (await store.get(job_id))["status"] == "done":
            break
        await asyncio.sleep(0.01)
    j = await store.get(job_id)
    assert j["status"] == "done" and j["result"] == {"rows": 1} and j["stage"] == "done"


@pytest.mark.asyncio
async def test_error_is_status_not_crash():
    store = InMemoryJobStore()
    runner = JobRunner(store)

    async def boom(stage):
        await stage("start")
        raise ValueError("нет провайдера")

    job_id = await runner.submit(boom)
    for _ in range(50):
        if (await store.get(job_id))["status"] == "error":
            break
        await asyncio.sleep(0.01)
    j = await store.get(job_id)
    assert j["status"] == "error" and "нет провайдера" in j["error"]
