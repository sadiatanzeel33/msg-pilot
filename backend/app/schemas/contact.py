"""Contact schemas."""

from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID
from datetime import datetime


class ContactCreate(BaseModel):
    name: str
    phone: str
    group_name: Optional[str] = None
    custom_message: Optional[str] = None
    tag_ids: Optional[List[UUID]] = []


class ContactResponse(BaseModel):
    id: UUID
    name: str
    phone: str
    group_name: Optional[str]
    custom_message: Optional[str]
    created_at: datetime
    tags: List[dict] = []

    class Config:
        from_attributes = True


class ContactBulkPreview(BaseModel):
    """Preview row from Excel upload."""
    row: int
    name: str
    phone: str
    message: Optional[str] = None
    valid: bool
    error: Optional[str] = None


class TagCreate(BaseModel):
    name: str


class TagResponse(BaseModel):
    id: UUID
    name: str

    class Config:
        from_attributes = True
