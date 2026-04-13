"""One-time Gmail OAuth2 setup — run this interactively to authorize access.

Usage:
    cd backend
    python setup_gmail.py

Prerequisites:
    1. Create a Google Cloud project at https://console.cloud.google.com/
    2. Enable the Gmail API
    3. Create OAuth2 credentials (Desktop application type)
    4. Download the credentials JSON and save as 'credentials.json' in backend/
"""

import sys
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]
CREDENTIALS_FILE = "credentials.json"
TOKEN_FILE = "token.json"


def main() -> None:
    creds = None
    token_path = Path(TOKEN_FILE)
    creds_path = Path(CREDENTIALS_FILE)

    # Load existing token if available
    if token_path.exists():
        creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)

    # If no valid creds, run the OAuth flow
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("Refreshing expired token...")
            creds.refresh(Request())
        else:
            if not creds_path.exists():
                print(f"ERROR: '{CREDENTIALS_FILE}' not found in {Path.cwd()}")
                print("Download OAuth2 credentials from Google Cloud Console first.")
                sys.exit(1)

            print("Opening browser for Gmail authorization...")
            flow = InstalledAppFlow.from_client_secrets_file(
                str(creds_path), SCOPES
            )
            creds = flow.run_local_server(port=0)

        # Save the token
        token_path.write_text(creds.to_json(), encoding="utf-8")
        print(f"Token saved to {token_path.resolve()}")

    print("Gmail OAuth2 setup complete!")
    print(f"Token file: {token_path.resolve()}")
    print("You can now enable GMAIL_ENABLED=true in your .env file.")


if __name__ == "__main__":
    main()
