FROM python:3.12-slim
ENV PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1
RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY pyproject.toml .
COPY app ./app
RUN pip install -e .
RUN useradd -m svc && mkdir -p /data && chown -R svc /app /data
USER svc
ENV CHROMA_PATH=/data/chroma
ENV PROJECT_ROOT=/app/project
EXPOSE 8020
HEALTHCHECK --interval=30s --timeout=5s CMD curl -fsS http://localhost:8020/health || exit 1
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8020"]
