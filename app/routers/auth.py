from fastapi import APIRouter, HTTPException

from app.config.settings import get_settings
from app.services.google_auth import (
    get_authorization_url,
    get_credentials,
    save_credentials,
)

router = APIRouter(prefix="/auth", tags=["auth"])
settings = get_settings()


@router.get("/google")
async def google_auth():
    """Get Google OAuth authorization URL."""
    return {"url": get_authorization_url()}


@router.get("/google/callback")
async def google_auth_callback(code: str, state: str = None):
    """Handle Google OAuth callback."""
    try:
        user_id = settings.TEST_USER_EMAIL
        credentials = get_credentials(code)
        save_credentials(credentials, user_id)
        return {"status": "success", "user_id": user_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
