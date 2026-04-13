"""Application settings loaded from environment variables / .env file."""

from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # ── Vault ────────────────────────────────────────────────────
    vault_path: str = "."

    # ── Gmail ────────────────────────────────────────────────────
    gmail_enabled: bool = False
    gmail_poll_interval_seconds: int = 120
    gmail_credentials_file: str = "credentials.json"
    gmail_token_file: str = "token.json"

    # ── Facebook ─────────────────────────────────────────────────
    facebook_enabled: bool = False
    facebook_poll_interval_seconds: int = 180
    facebook_page_access_token: str = ""
    facebook_page_id: str = ""

    # ── Server ───────────────────────────────────────────────────
    host: str = "127.0.0.1"
    port: int = 8000

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}

    # ── Derived paths ────────────────────────────────────────────
    @property
    def vault_root(self) -> Path:
        return Path(self.vault_path)

    @property
    def needs_action_dir(self) -> Path:
        return self.vault_root / "Needs_Action"

    @property
    def logs_dir(self) -> Path:
        return self.vault_root / "Logs"

    @property
    def seen_ids_path(self) -> Path:
        return Path(__file__).resolve().parent.parent / "data" / "seen_ids.json"

    def ensure_directories(self) -> None:
        """Create vault subdirectories if they don't exist."""
        for d in [
            self.needs_action_dir,
            self.logs_dir,
            self.vault_root / "Plans",
            self.vault_root / "Pending_Approval",
            self.vault_root / "Approved",
            self.vault_root / "Rejected",
            self.vault_root / "Done",
        ]:
            d.mkdir(parents=True, exist_ok=True)
        # Ensure data dir for seen_ids.json
        self.seen_ids_path.parent.mkdir(parents=True, exist_ok=True)


settings = Settings()
