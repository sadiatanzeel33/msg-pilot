"""Activity logs and WhatsApp session endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from uuid import UUID
from pydantic import BaseModel
from datetime import datetime

from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.activity_log import ActivityLog

router = APIRouter(prefix="/logs", tags=["Logs"])


class LogResponse(BaseModel):
    id: UUID
    action: str
    detail: str | None
    created_at: datetime

    class Config:
        from_attributes = True


@router.get("/", response_model=List[LogResponse])
async def list_logs(skip: int = 0, limit: int = 100, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(ActivityLog).where(ActivityLog.user_id == user.id)
        .order_by(ActivityLog.created_at.desc()).offset(skip).limit(limit)
    )
    return result.scalars().all()
