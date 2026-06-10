import pytest
from pydantic import BaseModel
from app.services.llm.base import ProviderInfo
from app.services.llm.structured import StructuredCallError, call_structured


class Out(BaseModel):
    material: str | None = None
    mass_kg: float | None = None


class FakeProvider:
    def __init__(self, answers):
        self.answers = list(answers)
        self.calls = 0
        self.info = ProviderInfo(id=1, name="fake", kind="local",
                                 base_url="x", model="m", enabled=True, priority=1)
    async def chat_text(self, prompt):
        self.calls += 1
        return self.answers.pop(0)
    async def chat_vision(self, prompt, image_b64):
        return await self.chat_text(prompt)


@pytest.mark.asyncio
async def test_valid_first_try():
    p = FakeProvider(['{"material":"Д16","mass_kg":0.42}'])
    out = await call_structured(p, "извлеки", Out)
    assert out.material == "Д16" and p.calls == 1


@pytest.mark.asyncio
async def test_repair_once_then_ok():
    p = FakeProvider(["мусор не json", '{"material":null,"mass_kg":null}'])
    out = await call_structured(p, "извлеки", Out)
    assert out.material is None and p.calls == 2


@pytest.mark.asyncio
async def test_fail_after_repair_keeps_raw():
    p = FakeProvider(["мусор", "опять мусор"])
    with pytest.raises(StructuredCallError) as e:
        await call_structured(p, "извлеки", Out)
    assert e.value.raw == "опять мусор" and p.calls == 2
