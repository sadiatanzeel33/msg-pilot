"""Campaign schemas."""

from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID
from datetime import datetime


class CampaignCreate(BaseModel):
    name: str
    message_template: str
    contact_ids: List[UUID] = []
    min_delay: int = 8
    max_delay: int = 25
    daily_limit: int = 500
    scheduled_at: Optional[datetime] = None


class CampaignUpdate(BaseModel):
    name: Optional[str] = None
    message_template: Optional[str] = None
    min_delay: Optional[int] = None
    max_delay: Optional[int] = None
    daily_limit: Optional[int] = None
    scheduled_at: Optional[datetime] = None


class CampaignContactResponse(BaseModel):
    id: UUID
    name: str
    phone: str
    status: str
    error_message: Optional[str]
    sent_at: Optional[datetime]

    class Config:
        from_attributes = True


class CampaignResponse(BaseModel):
    id: UUID
    name: str
    message_template: str
    status: str
    min_delay: int
    max_delay: int
    daily_limit: int
    scheduled_at: Optional[datetime]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    created_at: datetime
    total_contacts: int = 0
    sent_count: int = 0
    failed_count: int = 0
    pending_count: int = 0

    class Config:
        from_attributes = True


class DashboardStats(BaseModel):
    total_campaigns: int
    total_contacts: int
    total_sent: int
    total_failed: int
    total_pending: int
    campaigns_today: int
    daily_sent_data: List[dict] = []
