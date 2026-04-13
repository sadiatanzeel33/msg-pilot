"""Creates markdown task files in the vault's /Needs_Action/ directory."""

import re
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from app.config import settings
from app.models.schemas import TaskItem

PKT = ZoneInfo("Asia/Karachi")


def _sanitize_filename(text: str) -> str:
    """Convert a title to a safe filename slug."""
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    return text[:80]


def create_task_file(task: TaskItem) -> Path:
    """Write a markdown task file into /Needs_Action/ and return the path."""
    settings.ensure_directories()

    now = datetime.now(PKT)
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%Y-%m-%d %H:%M PKT")
    slug = _sanitize_filename(task.title)
    filename = f"{date_str}_{slug}.md"
    filepath = settings.needs_action_dir / filename

    # Avoid overwriting — append a counter if file exists
    counter = 1
    while filepath.exists():
        counter += 1
        filepath = settings.needs_action_dir / f"{date_str}_{slug}-{counter}.md"

    # Build detail lines
    detail_lines = ""
    for key, value in task.details.items():
        detail_lines += f"- **{key}:** {value}\n"

    content = f"""# Task: {task.title}

**Source:** {task.source}
**Date:** {date_str}
**Priority:** {task.priority}

## Details
{detail_lines.rstrip()}

## Required Action
{task.required_action}
"""

    filepath.write_text(content, encoding="utf-8")
    return filepath
