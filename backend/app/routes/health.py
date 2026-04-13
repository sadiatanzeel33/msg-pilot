"""Health check endpoint."""

from fastapi import APIRouter

from app.models.schemas import HealthResponse, HealthStatus, WatcherState

router = APIRouter()

# These will be set by main.py after watcher initialization
_watchers: dict = {}
_start_time: float = 0


def configure(watchers: dict, start_time: float) -> None:
    global _watchers, _start_time
    _watchers = watchers
    _start_time = start_time


@router.get("/health", response_model=HealthResponse)
async def health():
    import time

    uptime = time.time() - _start_time
    watcher_statuses = {name: w.get_status() for name, w in _watchers.items()}

    # Determine overall status
    states = [w.state for w in watcher_statuses.values() if w.enabled]
    if not states:
        status = HealthStatus.healthy
    elif all(s == WatcherState.running for s in states):
        status = HealthStatus.healthy
    elif all(s == WatcherState.error for s in states):
        status = HealthStatus.unhealthy
    else:
        status = HealthStatus.degraded

    return HealthResponse(
        status=status,
        uptime_seconds=round(uptime, 1),
        watchers=watcher_statuses,
    )
