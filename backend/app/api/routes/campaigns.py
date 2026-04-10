"""Campaign management endpoints."""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from typing import List
from uuid import UUID
from datetime import datetime, timezone
import os, io, uuid as uuid_mod, aiofiles

from app.core.database import get_db
from app.core.config import settings
from app.api.deps import get_current_user
from app.models.user import User
from app.models.contact import Contact
from app.models.campaign import Campaign, CampaignContact, CampaignMedia, CampaignStatus, MessageStatus
from app.models.activity_log import ActivityLog
from app.schemas.campaign import CampaignCreate, CampaignUpdate, CampaignResponse, CampaignContactResponse
from app.utils.excel import export_campaign_report

router = APIRouter(prefix="/campaigns", tags=["Campaigns"])


def _campaign_stats(campaign: Campaign) -> dict:
    contacts = campaign.contacts or []
    sent = sum(1 for c in contacts if c.status == MessageStatus.SENT)
    failed = sum(1 for c in contacts if c.status == MessageStatus.FAILED)
    pending = sum(1 for c in contacts if c.status == MessageStatus.PENDING)
    return {
        "total_contacts": len(contacts), "sent_count": sent,
        "failed_count": failed, "pending_count": pending,
    }


@router.post("/", response_model=CampaignResponse, status_code=201)
async def create_campaign(body: CampaignCreate, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    campaign = Campaign(
        user_id=user.id, name=body.name, message_template=body.message_template,
        min_delay=body.min_delay, max_delay=body.max_delay, daily_limit=body.daily_limit,
        scheduled_at=body.scheduled_at,
        status=CampaignStatus.SCHEDULED if body.scheduled_at else CampaignStatus.DRAFT,
    )
    db.add(campaign)
    await db.flush()

    # Attach contacts
    if body.contact_ids:
        result = await db.execute(select(Contact).where(Contact.id.in_(body.contact_ids), Contact.user_id == user.id))
        contacts = result.scalars().all()
        seen_phones = set()
        for c in contacts:
            if c.phone in seen_phones:
                continue
            seen_phones.add(c.phone)
            msg = body.message_template.replace("{Name}", c.name).replace("{name}", c.name)
            if c.custom_message:
                msg = c.custom_message.replace("{Name}", c.name)
            db.add(CampaignContact(
                campaign_id=campaign.id, contact_id=c.id,
                name=c.name, phone=c.phone, personalized_message=msg,
            ))
        await db.flush()

    # Log
    db.add(ActivityLog(user_id=user.id, action="campaign_created", detail=f"Campaign '{body.name}' created"))

    # Reload with contacts
    result = await db.execute(
        select(Campaign).options(selectinload(Campaign.contacts)).where(Campaign.id == campaign.id)
    )
    campaign = result.scalar_one()
    stats = _campaign_stats(campaign)
    return CampaignResponse(
        id=campaign.id, name=campaign.name, message_template=campaign.message_template,
        status=campaign.status.value, min_delay=campaign.min_delay, max_delay=campaign.max_delay,
        daily_limit=campaign.daily_limit, scheduled_at=campaign.scheduled_at,
        started_at=campaign.started_at, completed_at=campaign.completed_at,
        created_at=campaign.created_at, **stats,
    )


@router.get("/", response_model=List[CampaignResponse])
async def list_campaigns(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Campaign).options(selectinload(Campaign.contacts))
        .where(Campaign.user_id == user.id).order_by(Campaign.created_at.desc())
    )
    campaigns = result.scalars().unique().all()
    out = []
    for c in campaigns:
        stats = _campaign_stats(c)
        out.append(CampaignResponse(
            id=c.id, name=c.name, message_template=c.message_template,
            status=c.status.value, min_delay=c.min_delay, max_delay=c.max_delay,
            daily_limit=c.daily_limit, scheduled_at=c.scheduled_at,
            started_at=c.started_at, completed_at=c.completed_at,
            created_at=c.created_at, **stats,
        ))
    return out


@router.get("/{campaign_id}", response_model=CampaignResponse)
async def get_campaign(campaign_id: UUID, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Campaign).options(selectinload(Campaign.contacts))
        .where(Campaign.id == campaign_id, Campaign.user_id == user.id)
    )
    c = result.scalar_one_or_none()
    if not c:
        raise HTTPException(status_code=404, detail="Campaign not found")
    stats = _campaign_stats(c)
    return CampaignResponse(
        id=c.id, name=c.name, message_template=c.message_template,
        status=c.status.value, min_delay=c.min_delay, max_delay=c.max_delay,
        daily_limit=c.daily_limit, scheduled_at=c.scheduled_at,
        started_at=c.started_at, completed_at=c.completed_at,
        created_at=c.created_at, **stats,
    )


@router.get("/{campaign_id}/contacts", response_model=List[CampaignContactResponse])
async def get_campaign_contacts(campaign_id: UUID, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(CampaignContact).join(Campaign).where(Campaign.id == campaign_id, Campaign.user_id == user.id)
    )
    return result.scalars().all()


# ── Actions: Start / Pause / Resume / Stop ──
@router.post("/{campaign_id}/start")
async def start_campaign(campaign_id: UUID, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Campaign).where(Campaign.id == campaign_id, Campaign.user_id == user.id))
    c = result.scalar_one_or_none()
    if not c:
        raise HTTPException(status_code=404)
    if c.status not in (CampaignStatus.DRAFT, CampaignStatus.SCHEDULED, CampaignStatus.PAUSED):
        raise HTTPException(status_code=400, detail=f"Cannot start campaign in '{c.status.value}' state")
    c.status = CampaignStatus.RUNNING
    c.started_at = c.started_at or datetime.now(timezone.utc)
    db.add(ActivityLog(user_id=user.id, action="campaign_started", detail=str(campaign_id)))

    # Trigger Celery task (gracefully skip if Celery/Redis unavailable)
    try:
        from app.services.celery_app import run_campaign_task
        run_campaign_task.delay(str(campaign_id))
    except Exception:
        return {"status": "running", "warning": "Campaign saved but message sending requires a background worker (Celery + Redis). Deploy with full infrastructure to enable sending."}

    return {"status": "running"}


@router.post("/{campaign_id}/pause")
async def pause_campaign(campaign_id: UUID, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Campaign).where(Campaign.id == campaign_id, Campaign.user_id == user.id))
    c = result.scalar_one_or_none()
    if not c or c.status != CampaignStatus.RUNNING:
        raise HTTPException(status_code=400, detail="Campaign is not running")
    c.status = CampaignStatus.PAUSED
    return {"status": "paused"}


@router.post("/{campaign_id}/stop")
async def stop_campaign(campaign_id: UUID, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Campaign).where(Campaign.id == campaign_id, Campaign.user_id == user.id))
    c = result.scalar_one_or_none()
    if not c:
        raise HTTPException(status_code=404)
    c.status = CampaignStatus.STOPPED
    c.completed_at = datetime.now(timezone.utc)
    return {"status": "stopped"}


# ── Media upload ──
@router.post("/{campaign_id}/media")
async def upload_media(campaign_id: UUID, file: UploadFile = File(...), user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Campaign).where(Campaign.id == campaign_id, Campaign.user_id == user.id))
    c = result.scalar_one_or_none()
    if not c:
        raise HTTPException(status_code=404)

    upload_dir = os.path.join(settings.UPLOAD_DIR, str(campaign_id))
    os.makedirs(upload_dir, exist_ok=True)
    ext = os.path.splitext(file.filename)[1]
    stored_name = f"{uuid_mod.uuid4()}{ext}"
    path = os.path.join(upload_dir, stored_name)
    async with aiofiles.open(path, "wb") as f:
        await f.write(await file.read())

    media = CampaignMedia(campaign_id=campaign_id, file_path=path, file_name=file.filename, mime_type=file.content_type or "application/octet-stream")
    db.add(media)
    await db.flush()
    return {"id": str(media.id), "file_name": file.filename}


# ── Export report ──
@router.get("/{campaign_id}/report")
async def download_report(campaign_id: UUID, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(CampaignContact).join(Campaign).where(Campaign.id == campaign_id, Campaign.user_id == user.id)
    )
    contacts = result.scalars().all()
    rows = [{"name": c.name, "phone": c.phone, "status": c.status.value, "sent_at": str(c.sent_at or ""), "error_message": c.error_message or ""} for c in contacts]
    xlsx = export_campaign_report(rows)
    return StreamingResponse(
        io.BytesIO(xlsx),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename=report_{campaign_id}.xlsx"},
    )
