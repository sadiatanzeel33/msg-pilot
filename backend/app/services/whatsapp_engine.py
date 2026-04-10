"""
WhatsApp Web automation engine using Playwright.

This module handles:
- QR code login and session persistence
- Sending text messages
- Sending media (images, PDFs, documents)
- Session reconnection without re-scanning
"""

import asyncio
import os
import logging
from typing import Optional
from app.core.config import settings

try:
    from playwright.async_api import async_playwright, Page, Browser, BrowserContext
except ImportError:
    async_playwright = None
    Page = None
    Browser = None
    BrowserContext = None

logger = logging.getLogger(__name__)

WA_URL = "https://web.whatsapp.com"


class WhatsAppEngine:
    """Manages a single WhatsApp Web session per user."""

    def __init__(self, user_id: str):
        self.user_id = user_id
        self.session_dir = os.path.join(settings.WA_SESSION_DIR, user_id)
        os.makedirs(self.session_dir, exist_ok=True)
        self._browser: Optional[Browser] = None
        self._context: Optional[BrowserContext] = None
        self._page: Optional[Page] = None

    async def _launch(self) -> Page:
        """Launch browser with persistent context (stores cookies/session)."""
        pw = await async_playwright().start()
        self._browser = await pw.chromium.launch(headless=settings.WA_HEADLESS)
        self._context = await self._browser.new_context(
            storage_state=self._state_path if os.path.exists(self._state_path) else None,
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        )
        self._page = await self._context.new_page()
        return self._page

    @property
    def _state_path(self) -> str:
        return os.path.join(self.session_dir, "state.json")

    async def _save_state(self):
        """Persist browser storage state for session reuse."""
        if self._context:
            await self._context.storage_state(path=self._state_path)

    async def get_qr_code(self) -> Optional[bytes]:
        """
        Navigate to WhatsApp Web and capture QR code screenshot.
        Returns PNG bytes or None if already logged in.
        """
        page = await self._launch()
        await page.goto(WA_URL, wait_until="networkidle", timeout=60000)

        # Check if already logged in (search bar present)
        try:
            await page.wait_for_selector('[data-testid="chat-list"]', timeout=10000)
            await self._save_state()
            await self.close()
            return None  # Already authenticated
        except Exception:
            pass

        # Wait for QR canvas
        try:
            qr_element = await page.wait_for_selector("canvas", timeout=30000)
            if qr_element:
                screenshot = await qr_element.screenshot()
                # Don't close — keep alive for scanning
                # Start background task to wait for login
                asyncio.create_task(self._wait_for_login(page))
                return screenshot
        except Exception as e:
            logger.error(f"QR capture failed: {e}")

        await self.close()
        return None

    async def _wait_for_login(self, page: Page):
        """Wait up to 120s for user to scan QR, then save session."""
        try:
            await page.wait_for_selector('[data-testid="chat-list"]', timeout=120000)
            await self._save_state()
            logger.info(f"WhatsApp session saved for user {self.user_id}")
        except Exception:
            logger.warning(f"QR scan timeout for user {self.user_id}")
        finally:
            await self.close()

    async def ensure_connected(self) -> Page:
        """Ensure we have an authenticated page. Raises if no session."""
        page = await self._launch()
        await page.goto(WA_URL, wait_until="networkidle", timeout=60000)

        try:
            await page.wait_for_selector('[data-testid="chat-list"]', timeout=30000)
            return page
        except Exception:
            await self.close()
            raise RuntimeError("WhatsApp session expired. Please re-scan QR code.")

    async def send_message(self, phone: str, message: str) -> bool:
        """
        Send a text message to a phone number via WhatsApp Web.
        Phone should be in E.164 format (e.g., +1234567890).
        """
        page = self._page
        if not page:
            page = await self.ensure_connected()

        # Remove + prefix for URL
        phone_clean = phone.lstrip("+")

        try:
            # Use WhatsApp's direct chat URL to avoid contact lookup issues
            url = f"https://web.whatsapp.com/send?phone={phone_clean}&text={message}"
            await page.goto(url, wait_until="networkidle", timeout=30000)

            # Wait for the send button to appear
            send_btn = await page.wait_for_selector(
                '[data-testid="send"], span[data-icon="send"]',
                timeout=15000,
            )
            if send_btn:
                await send_btn.click()
                await asyncio.sleep(2)  # Wait for message to be sent
                return True

        except Exception as e:
            logger.error(f"Failed to send to {phone}: {e}")

            # Check for "Phone number shared via url is invalid" popup
            try:
                invalid = await page.query_selector('div[data-testid="popup-contents"]')
                if invalid:
                    logger.warning(f"Invalid number detected: {phone}")
                    # Click OK to dismiss
                    ok_btn = await page.query_selector('div[data-testid="popup-controls"] button')
                    if ok_btn:
                        await ok_btn.click()
            except Exception:
                pass

            return False

        return False

    async def send_media(self, phone: str, file_path: str, caption: str = "") -> bool:
        """
        Send a media file (image, PDF, document) to a phone number.
        """
        page = self._page
        if not page:
            page = await self.ensure_connected()

        phone_clean = phone.lstrip("+")

        try:
            await page.goto(f"https://web.whatsapp.com/send?phone={phone_clean}", wait_until="networkidle", timeout=30000)

            # Wait for chat to load
            await page.wait_for_selector('[data-testid="conversation-compose-box-input"]', timeout=15000)

            # Click attachment button
            attach_btn = await page.wait_for_selector('[data-testid="clip"]', timeout=5000)
            if attach_btn:
                await attach_btn.click()
                await asyncio.sleep(1)

            # Upload file via the document input
            file_input = await page.wait_for_selector('input[accept="*"]', timeout=5000)
            if file_input:
                await file_input.set_input_files(file_path)
                await asyncio.sleep(2)

            # Add caption if provided
            if caption:
                caption_box = await page.query_selector('[data-testid="media-caption-input-container"] [contenteditable="true"]')
                if caption_box:
                    await caption_box.fill(caption)

            # Click send
            send_btn = await page.wait_for_selector('[data-testid="send"]', timeout=10000)
            if send_btn:
                await send_btn.click()
                await asyncio.sleep(3)
                return True

        except Exception as e:
            logger.error(f"Failed to send media to {phone}: {e}")

        return False

    async def close(self):
        """Clean up browser resources."""
        try:
            if self._context:
                await self._save_state()
            if self._browser:
                await self._browser.close()
        except Exception:
            pass
        self._browser = None
        self._context = None
        self._page = None
