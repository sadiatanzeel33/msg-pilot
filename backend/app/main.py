"""FastAPI application with watcher lifecycle management."""

import logging
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.config import settings
from app.routes import dashboard, health, publish, status
from app.services.duplicate_detector import DuplicateDetector
from app.watchers.facebook_watcher import FacebookWatcher
from app.watchers.gmail_watcher import GmailWatcher

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)-25s | %(levelname)-7s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# ── Shared state ─────────────────────────────────────────────
start_time: float = 0
dedup = DuplicateDetector()
watchers: dict = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Start watchers on startup, stop them on shutdown."""
    global start_time, watchers

    start_time = time.time()
    settings.ensure_directories()

    logger.info("Vault path: %s", settings.vault_root)
    logger.info("Gmail enabled: %s", settings.gmail_enabled)
    logger.info("Facebook enabled: %s", settings.facebook_enabled)

    # Initialize watchers
    gmail = GmailWatcher(dedup)
    facebook = FacebookWatcher(dedup)
    watchers = {"gmail": gmail, "facebook": facebook}

    # Configure routes with shared state
    health.configure(watchers, start_time)
    status.configure(watchers, start_time)
    dashboard.configure(watchers, start_time)

    # Start enabled watchers
    for w in watchers.values():
        await w.start()

    logger.info("AI-FTE Watchers backend started.")

    yield

    # Shutdown
    logger.info("Shutting down watchers...")
    for w in watchers.values():
        await w.stop()

    # Close Facebook HTTP client
    if hasattr(facebook, "close"):
        await facebook.close()

    logger.info("AI-FTE Watchers backend stopped.")


# ── App ──────────────────────────────────────────────────────
app = FastAPI(
    title="AI-FTE Watchers",
    description="Gmail & Facebook watchers for the AI-FTE Obsidian vault",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(health.router)
app.include_router(status.router)
app.include_router(dashboard.router)
app.include_router(publish.router)
