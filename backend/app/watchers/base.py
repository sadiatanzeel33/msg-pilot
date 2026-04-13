"""Abstract base watcher with async polling loop, backoff, and status tracking."""

import asyncio
import logging
from abc import ABC, abstractmethod
from datetime import datetime
from zoneinfo import ZoneInfo

from app.models.schemas import WatcherState, WatcherStatus

PKT = ZoneInfo("Asia/Karachi")
logger = logging.getLogger(__name__)

MAX_BACKOFF_MULTIPLIER = 5


class BaseWatcher(ABC):
    """Base class for all watchers. Subclasses implement `poll()` and `name`."""

    def __init__(self, poll_interval: int, enabled: bool) -> None:
        self.poll_interval = poll_interval
        self.enabled = enabled
        self.state = WatcherState.disabled if not enabled else WatcherState.stopped
        self.last_poll: datetime | None = None
        self.last_error: str | None = None
        self.tasks_created: int = 0
        self.consecutive_errors: int = 0
        self._task: asyncio.Task | None = None

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable watcher name."""

    @abstractmethod
    async def poll(self) -> int:
        """Execute one polling cycle. Return number of new tasks created."""

    def get_status(self) -> WatcherStatus:
        return WatcherStatus(
            name=self.name,
            enabled=self.enabled,
            state=self.state,
            last_poll=self.last_poll,
            last_error=self.last_error,
            tasks_created=self.tasks_created,
            consecutive_errors=self.consecutive_errors,
            poll_interval_seconds=self.poll_interval,
        )

    async def start(self) -> None:
        """Start the polling loop as a background task."""
        if not self.enabled:
            logger.info("%s is disabled, skipping start.", self.name)
            return
        self.state = WatcherState.running
        self._task = asyncio.create_task(self._loop())
        logger.info("%s started (interval=%ds).", self.name, self.poll_interval)

    async def stop(self) -> None:
        """Cancel the polling loop."""
        if self._task and not self._task.done():
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        self.state = WatcherState.stopped
        logger.info("%s stopped.", self.name)

    async def _loop(self) -> None:
        """Polling loop with exponential backoff on errors."""
        while True:
            try:
                new_tasks = await self.poll()
                self.last_poll = datetime.now(PKT)
                self.tasks_created += new_tasks
                self.consecutive_errors = 0
                self.last_error = None
                self.state = WatcherState.running

                await asyncio.sleep(self.poll_interval)

            except asyncio.CancelledError:
                raise
            except Exception as exc:
                self.consecutive_errors += 1
                self.last_error = str(exc)
                self.state = WatcherState.error
                logger.exception(
                    "%s poll error (#%d): %s",
                    self.name,
                    self.consecutive_errors,
                    exc,
                )

                backoff = min(
                    self.consecutive_errors, MAX_BACKOFF_MULTIPLIER
                ) * self.poll_interval
                await asyncio.sleep(backoff)
