from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api import addin, admin, auth, health, jobs, rag
from app.core.config import settings
from app.services import clients_monitor, job_store


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Старт: схема БД (create_all), журнал заданий, снапшот клиентов; стоп: снапшот."""
    from app.db.session import init_db

    await init_db()
    job_store.load_persisted()
    clients_monitor.load_persisted()
    yield
    clients_monitor.flush()


app = FastAPI(title="МАТНОРМ backend (каркас)", version="0.1.0", lifespan=lifespan)


@app.middleware("http")
async def track_clients(request: Request, call_next) -> Response:
    """Учёт подключений клиентов (ПК с Excel) по /api/* и /addin/* (SEC-002: только IP/UA)."""
    path = request.url.path
    if (path.startswith("/api/") or path.startswith("/addin")) and request.client:
        # За обратным прокси реальный IP приходит в X-Forwarded-For
        # (uvicorn --proxy-headers подставляет его в request.client.host).
        clients_monitor.record_request(
            ip=request.client.host,
            path=path,
            user_agent=request.headers.get("user-agent"),
        )
    return await call_next(request)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_origin_regex=settings.cors_origin_regex,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Статика надстройки Excel — единый origin с API (tunnel → :8123/addin/).
_addin_dir = Path(__file__).resolve().parent.parent.parent / "addin"
if _addin_dir.is_dir():
    app.mount("/addin", StaticFiles(directory=str(_addin_dir), html=True), name="addin")

app.include_router(health.router)
app.include_router(auth.router)
app.include_router(jobs.router)
app.include_router(addin.router)
app.include_router(admin.router)
app.include_router(rag.router)
