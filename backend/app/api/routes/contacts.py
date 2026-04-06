"""Contact management endpoints."""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload
from typing import List
from uuid import UUID
import io

from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.contact import Contact, Tag
from app.schemas.contact import (
    ContactCreate, ContactResponse, ContactBulkPreview,
    TagCreate, TagResponse,
)
from app.utils.excel import parse_contacts_excel, export_contacts_excel
from app.utils.phone import validate_phone

router = APIRouter(prefix="/contacts", tags=["Contacts"])


# ── Tags ──
@router.post("/tags", response_model=TagResponse, status_code=201)
async def create_tag(body: TagCreate, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    tag = Tag(name=body.name, user_id=user.id)
    db.add(tag)
    await db.flush()
    return tag


@router.get("/tags", response_model=List[TagResponse])
async def list_tags(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Tag).where(Tag.user_id == user.id))
    return result.scalars().all()


# ── Contacts CRUD ──
@router.post("/", response_model=ContactResponse, status_code=201)
async def create_contact(body: ContactCreate, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    valid, phone, err = validate_phone(body.phone)
    if not valid:
        raise HTTPException(status_code=400, detail=f"Invalid phone: {err}")

    contact = Contact(user_id=user.id, name=body.name, phone=phone, group_name=body.group_name, custom_message=body.custom_message)

    if body.tag_ids:
        tags = (await db.execute(select(Tag).where(Tag.id.in_(body.tag_ids), Tag.user_id == user.id))).scalars().all()
        contact.tags = list(tags)

    db.add(contact)
    await db.flush()
    return ContactResponse(
        id=contact.id, name=contact.name, phone=contact.phone,
        group_name=contact.group_name, custom_message=contact.custom_message,
        created_at=contact.created_at, tags=[{"id": str(t.id), "name": t.name} for t in contact.tags],
    )


@router.get("/", response_model=List[ContactResponse])
async def list_contacts(
    group: str = None, tag: str = None, search: str = None,
    skip: int = 0, limit: int = 100,
    user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db),
):
    q = select(Contact).options(selectinload(Contact.tags)).where(Contact.user_id == user.id)
    if group:
        q = q.where(Contact.group_name == group)
    if search:
        q = q.where(Contact.name.ilike(f"%{search}%") | Contact.phone.ilike(f"%{search}%"))
    if tag:
        q = q.join(Contact.tags).where(Tag.name == tag)
    q = q.offset(skip).limit(limit)
    result = await db.execute(q)
    contacts = result.scalars().unique().all()
    return [
        ContactResponse(
            id=c.id, name=c.name, phone=c.phone, group_name=c.group_name,
            custom_message=c.custom_message, created_at=c.created_at,
            tags=[{"id": str(t.id), "name": t.name} for t in c.tags],
        ) for c in contacts
    ]


@router.delete("/{contact_id}", status_code=204)
async def delete_contact(contact_id: UUID, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    await db.execute(delete(Contact).where(Contact.id == contact_id, Contact.user_id == user.id))


# ── Excel Upload / Preview ──
@router.post("/upload/preview", response_model=List[ContactBulkPreview])
async def preview_upload(file: UploadFile = File(...), user: User = Depends(get_current_user)):
    if not file.filename.endswith(".xlsx"):
        raise HTTPException(status_code=400, detail="Only .xlsx files are supported")
    content = await file.read()
    return parse_contacts_excel(content)


@router.post("/upload/confirm")
async def confirm_upload(
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Parse Excel again and insert valid contacts."""
    content = await file.read()
    previews = parse_contacts_excel(content)

    # Duplicate detection
    existing_phones = set()
    result = await db.execute(select(Contact.phone).where(Contact.user_id == user.id))
    for row in result:
        existing_phones.add(row[0])

    created, skipped, errors = 0, 0, 0
    for p in previews:
        if not p.valid:
            errors += 1
            continue
        if p.phone in existing_phones:
            skipped += 1
            continue
        db.add(Contact(user_id=user.id, name=p.name, phone=p.phone, custom_message=p.message))
        existing_phones.add(p.phone)
        created += 1

    return {"created": created, "skipped_duplicates": skipped, "errors": errors}


# ── Export ──
@router.get("/export")
async def export(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Contact).options(selectinload(Contact.tags)).where(Contact.user_id == user.id)
    )
    contacts = result.scalars().unique().all()
    data = [{"name": c.name, "phone": c.phone, "group_name": c.group_name, "tags": ",".join(t.name for t in c.tags)} for c in contacts]
    xlsx_bytes = export_contacts_excel(data)
    return StreamingResponse(
        io.BytesIO(xlsx_bytes),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=contacts.xlsx"},
    )
