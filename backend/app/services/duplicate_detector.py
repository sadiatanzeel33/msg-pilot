"""JSON-based duplicate detection with 7-day TTL auto-pruning."""

import json
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

from app.config import settings

PKT = ZoneInfo("Asia/Karachi")
TTL_DAYS = 7


class DuplicateDetector:
    """Tracks seen message IDs to prevent duplicate task creation."""

    def __init__(self) -> None:
        self._path: Path = settings.seen_ids_path
        self._seen: dict[str, str] = {}
        self._load()

    def _load(self) -> None:
        """Load seen IDs from disk."""
        if self._path.exists():
            try:
                data = json.loads(self._path.read_text(encoding="utf-8"))
                self._seen = data if isinstance(data, dict) else {}
            except (json.JSONDecodeError, OSError):
                self._seen = {}
        self._prune()

    def _save(self) -> None:
        """Persist seen IDs to disk."""
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._path.write_text(
            json.dumps(self._seen, indent=2), encoding="utf-8"
        )

    def _prune(self) -> None:
        """Remove entries older than TTL_DAYS."""
        cutoff = datetime.now(PKT) - timedelta(days=TTL_DAYS)
        cutoff_str = cutoff.isoformat()
        self._seen = {
            k: v for k, v in self._seen.items() if v > cutoff_str
        }
        self._save()

    def is_seen(self, source: str, item_id: str) -> bool:
        """Check if an item has already been processed."""
        key = f"{source}:{item_id}"
        return key in self._seen

    def mark_seen(self, source: str, item_id: str) -> None:
        """Record an item as processed."""
        key = f"{source}:{item_id}"
        self._seen[key] = datetime.now(PKT).isoformat()
        self._save()
