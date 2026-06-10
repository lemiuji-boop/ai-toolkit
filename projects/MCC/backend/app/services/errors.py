"""Явные ошибки сервисов с кодами причин (TZ-FINAL §3 — без заглушек)."""


class ServiceError(RuntimeError):
    code: str = "SERVICE_ERROR"

    def __init__(self, message: str, *, code: str | None = None):
        super().__init__(message)
        if code is not None:
            self.code = code


class VisionUnavailableError(ServiceError):
    code = "VISION_UNAVAILABLE"


class GeometryUnavailableError(ServiceError):
    code = "GEOMETRY_UNAVAILABLE"
