"""Gmail API watcher — polls for new emails and creates task files."""

import base64
import logging
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

from app.config import settings
from app.models.schemas import TaskItem
from app.services.duplicate_detector import DuplicateDetector
from app.services.logger_service import write_log
from app.services.vault_writer import create_task_file
from app.watchers.base import BaseWatcher

logger = logging.getLogger(__name__)

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]
SOURCE = "Gmail API"


class GmailWatcher(BaseWatcher):
    """Polls Gmail for unread messages and creates task files."""

    def __init__(self, dedup: DuplicateDetector) -> None:
        super().__init__(
            poll_interval=settings.gmail_poll_interval_seconds,
            enabled=settings.gmail_enabled,
        )
        self._dedup = dedup
        self._service = None

    @property
    def name(self) -> str:
        return "Gmail"

    def _get_service(self):
        """Build or refresh the Gmail API service."""
        if self._service is not None:
            return self._service

        token_path = Path(settings.gmail_token_file)
        creds = None

        if token_path.exists():
            creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
                token_path.write_text(creds.to_json(), encoding="utf-8")
            else:
                raise RuntimeError(
                    "Gmail token not found or invalid. Run setup_gmail.py first."
                )

        self._service = build("gmail", "v1", credentials=creds)
        return self._service

    async def poll(self) -> int:
        """Fetch unread emails and create tasks for new ones."""
        import asyncio

        service = await asyncio.to_thread(self._get_service)

        # Fetch unread messages
        results = await asyncio.to_thread(
            lambda: service.users()
            .messages()
            .list(userId="me", q="is:unread", maxResults=10)
            .execute()
        )

        messages = results.get("messages", [])
        if not messages:
            return 0

        created = 0
        for msg_stub in messages:
            msg_id = msg_stub["id"]

            if self._dedup.is_seen("gmail", msg_id):
                continue

            # Fetch full message
            msg = await asyncio.to_thread(
                lambda mid=msg_id: service.users()
                .messages()
                .get(userId="me", id=mid, format="metadata")
                .execute()
            )

            headers = {
                h["name"]: h["value"]
                for h in msg.get("payload", {}).get("headers", [])
            }
            sender = headers.get("From", "Unknown")
            subject = headers.get("Subject", "(no subject)")
            snippet = msg.get("snippet", "")

            # Determine priority based on labels
            labels = msg.get("labelIds", [])
            priority = "High" if "IMPORTANT" in labels else "Medium"

            task = TaskItem(
                source=SOURCE,
                title=f"Email from {sender.split('<')[0].strip()} - {subject}",
                priority=priority,
                details={
                    "From": sender,
                    "Subject": subject,
                    "Message ID": msg_id,
                    "Snippet": f'"{snippet[:200]}"',
                },
                required_action="Review and respond to this email.",
                raw_id=msg_id,
            )

            filepath = create_task_file(task)
            self._dedup.mark_seen("gmail", msg_id)
            created += 1

            write_log(
                action=f"Gmail task created - {subject}",
                source=SOURCE,
                details=[
                    f"From: {sender}",
                    f"Subject: {subject}",
                    f"Task file: {filepath.name}",
                ],
            )
            logger.info("Created task for email: %s", subject)

        return created
