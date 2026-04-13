"""Publish endpoints — post Eid campaign content to Facebook."""

from datetime import datetime
from zoneinfo import ZoneInfo

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.facebook_publisher import FacebookPublisher

router = APIRouter(prefix="/publish", tags=["publish"])

PKT = ZoneInfo("Asia/Karachi")
publisher = FacebookPublisher()

# ── Pre-loaded Eid Campaign Posts ────────────────────────────

EID_CAMPAIGN_POSTS = {
    "day4-countdown": {
        "title": "Day 4 — Countdown Post (March 4)",
        "message": (
            "\U0001f4e2 2 DAYS TO GO!\n\n"
            "Areesha's Collection Eid 2026 is almost here.\n\n"
            "Stitched. Unstitched. Statement pieces.\n\n"
            "Mark your calendars: March 6 \u2014 Full Collection Reveal \U0001f5d3\ufe0f\n\n"
            "Tag someone who NEEDS to see this! \U0001f447\n\n"
            "#AreeshasCollection #EidCountdown #2DaysToGo #PakistaniDresses #Eid2026"
        ),
    },
    "day5-final-teaser": {
        "title": "Day 5 — Final Teaser (March 5)",
        "message": (
            "TOMORROW. \U0001f5a4\n\n"
            "The wait is almost over.\n\n"
            "Areesha's Collection Eid 2026 \u2014 Dropping March 6\n\n"
            "Are you ready?\n\n"
            "\U0001f4ac Drop a \U0001f90d if you're excited!\n\n"
            "#AreeshasCollection #Tomorrow #EidCollection2026 #LaunchDay"
        ),
    },
    "day6-collection-reveal": {
        "title": "Day 6 — Collection Reveal (March 6)",
        "message": (
            "\U0001f389 IT'S HERE!\n\n"
            "Areesha's Collection \u2014 Eid 2026\n\n"
            "Stitched & Unstitched. Designed for the woman who owns every room she walks into.\n\n"
            "\U0001f6cd\ufe0f Browse our collection on this page!\n"
            "\U0001f4ac DM us to order or WhatsApp to place your order\n\n"
            "\U0001f69a Early Bird Offer: FREE DELIVERY on all orders before March 15!\n\n"
            "#AreeshasCollection #Eid2026 #EidCollection #NowLive #PakistaniFashion #WomensClothing #Karachi #EidOutfit"
        ),
    },
}


# ── Request / Response Models ────────────────────────────────

class PublishRequest(BaseModel):
    post_key: str
    custom_message: str | None = None


class PublishResponse(BaseModel):
    success: bool
    post_id: str
    title: str
    published_at: str


# ── Endpoints ────────────────────────────────────────────────

@router.get("/campaigns")
async def list_campaigns():
    """List all available pre-loaded campaign posts."""
    return {
        key: {"title": val["title"], "message_preview": val["message"][:150] + "..."}
        for key, val in EID_CAMPAIGN_POSTS.items()
    }


@router.post("/facebook", response_model=PublishResponse)
async def publish_to_facebook(req: PublishRequest):
    """Publish a campaign post to the Facebook Page.

    Use `post_key` to select a pre-loaded campaign post (e.g. 'day4-countdown'),
    or provide `custom_message` to override.
    """
    campaign = EID_CAMPAIGN_POSTS.get(req.post_key)
    if not campaign and not req.custom_message:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown post_key '{req.post_key}'. Use GET /publish/campaigns to see available posts.",
        )

    message = req.custom_message or campaign["message"]
    title = campaign["title"] if campaign else "Custom Post"

    try:
        result = await publisher.publish_post(message)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Facebook API error: {exc}")

    return PublishResponse(
        success=True,
        post_id=result["id"],
        title=title,
        published_at=datetime.now(PKT).strftime("%Y-%m-%d %H:%M PKT"),
    )
