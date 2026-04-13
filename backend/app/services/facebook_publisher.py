"""Facebook Graph API publisher — posts content to a Facebook Page."""

import logging
from datetime import datetime
from zoneinfo import ZoneInfo

import httpx

from app.config import settings
from app.services.logger_service import write_log

logger = logging.getLogger(__name__)

PKT = ZoneInfo("Asia/Karachi")
GRAPH_API_BASE = "https://graph.facebook.com/v19.0"


class FacebookPublisher:
    """Publishes posts to a Facebook Page via the Graph API."""

    def __init__(self) -> None:
        self._client = httpx.AsyncClient(timeout=30)

    async def publish_post(self, message: str) -> dict:
        """Publish a text post to the configured Facebook Page.

        Args:
            message: The post text content.

        Returns:
            Dict with 'id' (post ID) and 'success' flag.
        """
        page_id = settings.facebook_page_id
        token = settings.facebook_page_access_token

        if not page_id or not token:
            raise RuntimeError(
                "FACEBOOK_PAGE_ID and FACEBOOK_PAGE_ACCESS_TOKEN must be set in .env"
            )

        url = f"{GRAPH_API_BASE}/{page_id}/feed"
        payload = {
            "message": message,
            "access_token": token,
        }

        resp = await self._client.post(url, data=payload)
        resp.raise_for_status()
        data = resp.json()

        post_id = data.get("id", "unknown")
        now_str = datetime.now(PKT).strftime("%Y-%m-%d %H:%M PKT")

        write_log(
            action=f"Facebook post published",
            source="Facebook Publisher",
            details=[
                f"Post ID: {post_id}",
                f"Time: {now_str}",
                f"Message preview: {message[:120]}...",
            ],
        )
        logger.info("Published Facebook post: %s", post_id)

        return {"id": post_id, "success": True}

    async def close(self) -> None:
        await self._client.aclose()
