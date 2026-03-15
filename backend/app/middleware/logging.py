from typing import Any


def build_request_log(method: str, path: str, status_code: int, duration_ms: float) -> dict[str, Any]:
    return {
        "method": method,
        "path": path,
        "status_code": status_code,
        "duration_ms": round(duration_ms, 2),
    }

