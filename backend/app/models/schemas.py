"""Pydantic models for API responses and internal data."""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel


# ── Enums ────────────────────────────────────────────────────

class HealthStatus(str, Enum):
    healthy = "healthy"
    degraded = "degraded"
    unhealthy = "unhealthy"


class WatcherState(str, Enum):
    running = "running"
    stopped = "stopped"
    error = "error"
    disabled = "disabled"


# ── Watcher Status ───────────────────────────────────────────

class WatcherStatus(BaseModel):
    name: str
    enabled: bool
    state: WatcherState
    last_poll: Optional[datetime] = None
    last_error: Optional[str] = None
    tasks_created: int = 0
    consecutive_errors: int = 0
    poll_interval_seconds: int = 0


# ── Health Response ──────────────────────────────────────────

class HealthResponse(BaseModel):
    status: HealthStatus
    uptime_seconds: float
    watchers: dict[str, WatcherStatus]


# ── Status Response ──────────────────────────────────────────

class StatusResponse(BaseModel):
    server_started: datetime
    uptime_seconds: float
    vault_path: str
    watchers: dict[str, WatcherStatus]


# ── Task Item (internal) ────────────────────────────────────

class TaskItem(BaseModel):
    source: str
    title: str
    priority: str = "Medium"
    details: dict[str, str] = {}
    required_action: str = ""
    raw_id: str = ""
