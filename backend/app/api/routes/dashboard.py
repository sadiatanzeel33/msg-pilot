"""Dashboard analytics endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, cast, Date
from datetime import datetime, timedelta, timezone

from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.contact import Contact
from app.models.campaign import Campaign, CampaignContact, MessageStatus
from app.schemas.campaign import DashboardStats

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/stats", response_model=DashboardStats)
async def get_stats(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    uid = user.id
    today = datetime.now(timezone.utc).date()

    total_campaigns = (await db.execute(
        select(func.count()).select_from(Campaign).where(Campaign.user_id == uid)
    )).scalar() or 0

    total_contacts = (await db.execute(
        select(func.count()).select_from(Contact).where(Contact.user_id == uid)
    )).scalar() or 0

    # Message stats
    base = select(CampaignContact).join(Campaign).where(Campaign.user_id == uid)
    total_sent = (await db.execute(
        select(func.count()).select_from(CampaignContact).join(Campaign)
        .where(Campaign.user_id == uid, CampaignContact.status == MessageStatus.SENT)
    )).scalar() or 0

    total_failed = (await db.execute(
        select(func.count()).select_from(CampaignContact).join(Campaign)
        .where(Campaign.user_id == uid, CampaignContact.status == MessageStatus.FAILED)
    )).scalar() or 0

    total_pending = (await db.execute(
        select(func.count()).select_from(CampaignContact).join(Campaign)
        .where(Campaign.user_id == uid, CampaignContact.status == MessageStatus.PENDING)
    )).scalar() or 0

    campaigns_today = (await db.execute(
        select(func.count()).select_from(Campaign)
        .where(Campaign.user_id == uid, cast(Campaign.created_at, Date) == today)
    )).scalar() or 0

    # Daily sent last 7 days
    daily = []
    for i in range(6, -1, -1):
        d = today - timedelta(days=i)
        count = (await db.execute(
            select(func.count()).select_from(CampaignContact).join(Campaign)
            .where(Campaign.user_id == uid, CampaignContact.status == MessageStatus.SENT, cast(CampaignContact.sent_at, Date) == d)
        )).scalar() or 0
        daily.append({"date": str(d), "count": count})

    return DashboardStats(
        total_campaigns=total_campaigns, total_contacts=total_contacts,
        total_sent=total_sent, total_failed=total_failed, total_pending=total_pending,
        campaigns_today=campaigns_today, daily_sent_data=daily,
    )
