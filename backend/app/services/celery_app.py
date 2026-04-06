"""
Celery worker for background campaign execution.

Run with: celery -A app.services.celery_app worker -l info -c 1
"""

import asyncio
import random
import logging
from datetime import datetime, timezone
from celery import Celery
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings
from app.models.campaign import Campaign, CampaignContact, CampaignMedia, CampaignStatus, MessageStatus
from app.models.activity_log import ActivityLog
from app.services.whatsapp_engine import WhatsAppEngine

logger = logging.getLogger(__name__)

# Create Celery app
celery_app = Celery(
    "msgpilot",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)
celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    task_track_started=True,
    worker_concurrency=1,  # Single worker — one browser at a time
)

# Synchronous DB session for Celery tasks
sync_engine = create_engine(settings.DATABASE_URL_SYNC)
SyncSession = sessionmaker(bind=sync_engine)


def _run_async(coro):
    """Run async code from sync Celery task."""
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


@celery_app.task(name="run_campaign", bind=True, max_retries=0)
def run_campaign_task(self, campaign_id: str):
    """
    Execute a campaign: iterate over pending contacts, send messages
    with random delays, respect daily limits, handle pause/stop.
    """
    db = SyncSession()
    engine: WhatsAppEngine | None = None

    try:
        campaign = db.execute(
            select(Campaign).where(Campaign.id == campaign_id)
        ).scalar_one_or_none()

        if not campaign:
            logger.error(f"Campaign {campaign_id} not found")
            return

        if campaign.status != CampaignStatus.RUNNING:
            logger.info(f"Campaign {campaign_id} is not in RUNNING state, skipping")
            return

        # Get user_id for WhatsApp session
        user_id = str(campaign.user_id)

        # Get pending contacts
        pending = db.execute(
            select(CampaignContact)
            .where(CampaignContact.campaign_id == campaign_id, CampaignContact.status == MessageStatus.PENDING)
        ).scalars().all()

        if not pending:
            campaign.status = CampaignStatus.COMPLETED
            campaign.completed_at = datetime.now(timezone.utc)
            db.commit()
            return

        # Get media files for this campaign
        media_files = db.execute(
            select(CampaignMedia).where(CampaignMedia.campaign_id == campaign_id)
        ).scalars().all()

        # Launch WhatsApp engine
        engine = WhatsAppEngine(user_id)
        _run_async(engine.ensure_connected())

        sent_today = 0

        for contact in pending:
            # Re-check campaign status (might have been paused/stopped)
            db.refresh(campaign)
            if campaign.status != CampaignStatus.RUNNING:
                logger.info(f"Campaign {campaign_id} was {campaign.status.value}, stopping execution")
                break

            # Daily limit check
            if sent_today >= campaign.daily_limit:
                logger.info(f"Daily limit ({campaign.daily_limit}) reached for campaign {campaign_id}")
                campaign.status = CampaignStatus.PAUSED
                db.add(ActivityLog(
                    user_id=campaign.user_id, action="campaign_daily_limit",
                    detail=f"Campaign paused: daily limit of {campaign.daily_limit} reached",
                ))
                db.commit()
                break

            try:
                # Send text message
                message = contact.personalized_message or campaign.message_template
                success = _run_async(engine.send_message(contact.phone, message))

                # Send media if any
                if success and media_files:
                    for mf in media_files:
                        _run_async(engine.send_media(contact.phone, mf.file_path, ""))

                if success:
                    contact.status = MessageStatus.SENT
                    contact.sent_at = datetime.now(timezone.utc)
                    sent_today += 1
                else:
                    contact.status = MessageStatus.FAILED
                    contact.error_message = "Send failed — possible invalid number or network error"

            except Exception as e:
                contact.status = MessageStatus.FAILED
                contact.error_message = str(e)[:500]
                logger.error(f"Error sending to {contact.phone}: {e}")

            db.commit()

            # Random delay between messages
            delay = random.uniform(campaign.min_delay, campaign.max_delay)
            logger.info(f"Sent to {contact.phone} ({contact.status.value}), waiting {delay:.1f}s")
            _run_async(asyncio.sleep(delay))

        # Check if all done
        db.refresh(campaign)
        remaining = db.execute(
            select(CampaignContact)
            .where(CampaignContact.campaign_id == campaign_id, CampaignContact.status == MessageStatus.PENDING)
        ).scalars().all()

        if not remaining and campaign.status == CampaignStatus.RUNNING:
            campaign.status = CampaignStatus.COMPLETED
            campaign.completed_at = datetime.now(timezone.utc)

        db.add(ActivityLog(
            user_id=campaign.user_id, action="campaign_execution_done",
            detail=f"Campaign {campaign_id}: {sent_today} sent this session",
        ))
        db.commit()

    except Exception as e:
        logger.error(f"Campaign task failed: {e}")
        try:
            if campaign:
                campaign.status = CampaignStatus.PAUSED
                db.add(ActivityLog(user_id=campaign.user_id, action="campaign_error", detail=str(e)[:500]))
                db.commit()
        except Exception:
            pass
    finally:
        if engine:
            _run_async(engine.close())
        db.close()


@celery_app.task(name="check_scheduled_campaigns")
def check_scheduled_campaigns():
    """Periodic task to start scheduled campaigns."""
    db = SyncSession()
    try:
        now = datetime.now(timezone.utc)
        campaigns = db.execute(
            select(Campaign).where(
                Campaign.status == CampaignStatus.SCHEDULED,
                Campaign.scheduled_at <= now,
            )
        ).scalars().all()

        for c in campaigns:
            c.status = CampaignStatus.RUNNING
            c.started_at = now
            db.commit()
            run_campaign_task.delay(str(c.id))
            logger.info(f"Auto-started scheduled campaign {c.id}")
    finally:
        db.close()


# Celery Beat schedule
celery_app.conf.beat_schedule = {
    "check-scheduled-campaigns": {
        "task": "check_scheduled_campaigns",
        "schedule": 60.0,  # Every minute
    },
}
