"""Writes audit log entries as markdown files in the vault's /Logs/ directory."""

import re
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from app.config import settings

PKT = ZoneInfo("Asia/Karachi")


def _sanitize_slug(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    return text[:60]


def write_log(action: str, source: str, details: list[str]) -> Path:
    """Create a log markdown file in /Logs/ and return the path.

    Args:
        action: Short description of the action (used as title).
        source: The watcher or component that triggered this.
        details: List of detail strings to include.
    """
    settings.ensure_directories()

    now = datetime.now(PKT)
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%Y-%m-%d %H:%M PKT")
    slug = _sanitize_slug(action)
    filename = f"{date_str}_{slug}.md"
    filepath = settings.logs_dir / filename

    # Avoid overwriting
    counter = 1
    while filepath.exists():
        counter += 1
        filepath = settings.logs_dir / f"{date_str}_{slug}-{counter}.md"

    detail_lines = "\n".join(f"- {d}" for d in details)

    content = f"""# Log: {action}

**Date:** {time_str}
**Source:** {source}

## Details
{detail_lines}
"""

    filepath.write_text(content, encoding="utf-8")
    return filepath
