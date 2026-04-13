"""Facebook Graph API watcher — polls page conversations and creates task files."""

import logging

import httpx

from app.config import settings
from app.models.schemas import TaskItem
from app.services.duplicate_detector import DuplicateDetector
from app.services.logger_service import write_log
from app.services.vault_writer import create_task_file
from app.watchers.base import BaseWatcher

logger = logging.getLogger(__name__)

SOURCE = "Facebook API"
GRAPH_API_BASE = "https://graph.facebook.com/v19.0"


class FacebookWatcher(BaseWatcher):
    """Polls Facebook Page conversations for new messages."""

    def __init__(self, dedup: DuplicateDetector) -> None:
        super().__init__(
            poll_interval=settings.facebook_poll_interval_seconds,
            enabled=settings.facebook_enabled,
        )
        self._dedup = dedup
        self._client = httpx.AsyncClient(timeout=30)

    @property
    def name(self) -> str:
        return "Facebook"

    async def poll(self) -> int:
        """Fetch recent page conversations and create tasks for new messages."""
        page_id = settings.facebook_page_id
        token = settings.facebook_page_access_token

        if not page_id or not token:
            raise RuntimeError(
                "FACEBOOK_PAGE_ID and FACEBOOK_PAGE_ACCESS_TOKEN must be set."
            )

        # Fetch conversations
        url = f"{GRAPH_API_BASE}/{page_id}/conversations"
        params = {
            "fields": "id,updated_time,participants,messages.limit(1){message,from,created_time}",
            "limit": 10,
            "access_token": token,
        }

        resp = await self._client.get(url, params=params)
        resp.raise_for_status()
        data = resp.json()

        conversations = data.get("data", [])
        if not conversations:
            return 0

        created = 0
        for conv in conversations:
            conv_id = conv["id"]
            messages = conv.get("messages", {}).get("data", [])
            if not messages:
                continue

            latest_msg = messages[0]
            msg_id = latest_msg.get("id", conv_id)

            if self._dedup.is_seen("facebook", msg_id):
                continue

            sender_name = latest_msg.get("from", {}).get("name", "Unknown")
            message_text = latest_msg.get("message", "(no message)")
            created_time = latest_msg.get("created_time", "")

            # Get participant names
            participants = conv.get("participants", {}).get("data", [])
            participant_names = ", ".join(
                p.get("name", "Unknown") for p in participants
            )

            task = TaskItem(
                source=SOURCE,
                title=f"Facebook message from {sender_name}",
                priority="Medium",
                details={
                    "From": sender_name,
                    "Participants": participant_names,
                    "Message": f'"{message_text[:300]}"',
                    "Received": created_time,
                    "Conversation ID": conv_id,
                },
                required_action="Review and respond to this Facebook message.",
                raw_id=msg_id,
            )

            filepath = create_task_file(task)
            self._dedup.mark_seen("facebook", msg_id)
            created += 1

            write_log(
                action=f"Facebook task created - {sender_name}",
                source=SOURCE,
                details=[
                    f"From: {sender_name}",
                    f"Message preview: {message_text[:100]}",
                    f"Task file: {filepath.name}",
                ],
            )
            logger.info("Created task for FB message from: %s", sender_name)

        return created

    async def close(self) -> None:
        """Close the HTTP client."""
        await self._client.aclose()
