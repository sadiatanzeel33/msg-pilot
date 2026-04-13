"""Detailed status endpoint."""

import time
from datetime import datetime
from zoneinfo import ZoneInfo

from fastapi import APIRouter

from app.config import settings
from app.models.schemas import StatusResponse

router = APIRouter()

PKT = ZoneInfo("Asia/Karachi")

_watchers: dict = {}
_start_time: float = 0


def configure(watchers: dict, start_time: float) -> None:
    global _watchers, _start_time
    _watchers = watchers
    _start_time = start_time


@router.get("/status", response_model=StatusResponse)
async def status():
    uptime = time.time() - _start_time
    watcher_statuses = {name: w.get_status() for name, w in _watchers.items()}

    return StatusResponse(
        server_started=datetime.fromtimestamp(_start_time, tz=PKT),
        uptime_seconds=round(uptime, 1),
        vault_path=str(settings.vault_root),
        watchers=watcher_statuses,
    )
