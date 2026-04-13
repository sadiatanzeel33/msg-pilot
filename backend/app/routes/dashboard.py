"""HTML dashboard endpoint."""

import time
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.config import settings

router = APIRouter()

PKT = ZoneInfo("Asia/Karachi")
templates = Jinja2Templates(
    directory=str(Path(__file__).resolve().parent.parent / "templates")
)

_watchers: dict = {}
_start_time: float = 0


def configure(watchers: dict, start_time: float) -> None:
    global _watchers, _start_time
    _watchers = watchers
    _start_time = start_time


@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    uptime = time.time() - _start_time
    watcher_statuses = {name: w.get_status() for name, w in _watchers.items()}

    # Count task files in Needs_Action
    needs_action = settings.needs_action_dir
    pending_tasks = len(list(needs_action.glob("*.md"))) if needs_action.exists() else 0

    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "server_started": datetime.fromtimestamp(_start_time, tz=PKT).strftime(
                "%Y-%m-%d %H:%M PKT"
            ),
            "uptime_hours": round(uptime / 3600, 1),
            "vault_path": str(settings.vault_root),
            "watchers": watcher_statuses,
            "pending_tasks": pending_tasks,
            "now": datetime.now(PKT).strftime("%Y-%m-%d %H:%M PKT"),
        },
    )
