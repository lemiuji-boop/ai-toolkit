# Copyright 2026 Rinat Ishmaev
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from fastapi import FastAPI

from app.api.analyze import router as analyze_router
from app.api.validate import router as validate_router
from app.services.llm_client import ollama_available, resolve_ollama_base_url

app = FastAPI(title="CED AI Agent")

app.include_router(analyze_router)
app.include_router(validate_router)


@app.get("/health")
async def health() -> dict[str, str | bool]:
    ollama_ok = ollama_available()
    return {
        "status": "ok",
        "ollama_url": resolve_ollama_base_url(),
        "ollama_available": ollama_ok,
    }
