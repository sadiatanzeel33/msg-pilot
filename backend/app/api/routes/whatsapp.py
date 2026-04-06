"""WhatsApp session management endpoints."""

from fastapi import APIRouter, Depends
from app.api.deps import get_current_user
from app.models.user import User
from app.services.whatsapp_engine import WhatsAppEngine
from app.core.config import settings
import os, base64

router = APIRouter(prefix="/whatsapp", tags=["WhatsApp"])


@router.get("/session/status")
async def session_status(user: User = Depends(get_current_user)):
    """Check if a stored session exists for this user."""
    session_dir = os.path.join(settings.WA_SESSION_DIR, str(user.id))
    has_session = os.path.isdir(session_dir) and any(os.listdir(session_dir))
    return {"has_session": has_session}


@router.post("/session/qr")
async def get_qr(user: User = Depends(get_current_user)):
    """
    Launch headless browser and return QR code as base64 PNG.
    The frontend displays this QR for the user to scan.
    """
    engine = WhatsAppEngine(str(user.id))
    qr_bytes = await engine.get_qr_code()
    if qr_bytes:
        return {"qr": base64.b64encode(qr_bytes).decode(), "status": "waiting_scan"}
    return {"qr": None, "status": "already_authenticated"}


@router.post("/session/logout")
async def logout_session(user: User = Depends(get_current_user)):
    """Delete stored session."""
    import shutil
    session_dir = os.path.join(settings.WA_SESSION_DIR, str(user.id))
    if os.path.isdir(session_dir):
        shutil.rmtree(session_dir)
    return {"status": "logged_out"}
