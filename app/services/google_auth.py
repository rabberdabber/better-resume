import json
import os
from functools import lru_cache
from pathlib import Path

from fastapi import HTTPException
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow

from app.config.settings import get_settings

settings = get_settings()

# OAuth 2.0 configuration
SCOPES = [
    "https://www.googleapis.com/auth/documents",
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]


def get_flow() -> Flow:
    """Create and return an OAuth flow instance."""
    client_config = {
        "web": {
            "client_id": settings.GOOGLE_CLIENT_ID,
            "client_secret": settings.GOOGLE_CLIENT_SECRET,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": [settings.GOOGLE_REDIRECT_URI],
        }
    }

    return Flow.from_client_config(
        client_config,
        scopes=settings.GOOGLE_SCOPES,
        redirect_uri=settings.GOOGLE_REDIRECT_URI,
    )


def get_authorization_url() -> str:
    """Generate the authorization URL for Google OAuth."""
    flow = get_flow()
    authorization_url, _ = flow.authorization_url(
        access_type="offline", include_granted_scopes="true"
    )
    return authorization_url


@lru_cache()
def get_credentials_config():
    """Load credentials configuration from file."""
    try:
        credentials_path = Path("credentials/google_credentials.json")

        if not credentials_path.exists():
            raise FileNotFoundError("Credentials file not found in credentials folder")

        with open(credentials_path, "r") as f:
            return json.load(f)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to load credentials configuration: {str(e)}",
        ) from e


def get_credentials(code: str) -> Credentials:
    """Exchange the authorization code for credentials."""
    try:
        flow = get_flow()
        flow.fetch_token(code=code)
        return flow.credentials
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Failed to get credentials: {str(e)}"
        )


async def get_google_credentials() -> Credentials:
    """
    FastAPI dependency for getting stored Google credentials.
    Used for authenticated endpoints.
    """
    try:
        user_id = settings.TEST_USER_EMAIL
        return load_credentials(user_id)
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Failed to load credentials: {str(e)}"
        )


def save_credentials(credentials: Credentials, user_id: str) -> None:
    """Save credentials to a file."""
    creds_dict = {
        "token": credentials.token,
        "refresh_token": credentials.refresh_token,
        "token_uri": credentials.token_uri,
        "client_id": credentials.client_id,
        "client_secret": credentials.client_secret,
        "scopes": credentials.scopes,
    }

    os.makedirs("credentials", exist_ok=True)
    with open(f"credentials/{user_id}.json", "w") as f:
        json.dump(creds_dict, f)


def load_credentials(user_id: str) -> Credentials:
    """Load credentials from a file."""
    try:
        with open(f"credentials/{user_id}.json", "r") as f:
            creds_dict = json.load(f)
        return Credentials(**creds_dict)
    except FileNotFoundError:
        raise HTTPException(status_code=401, detail="Credentials not found")
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to load credentials: {str(e)}"
        )
