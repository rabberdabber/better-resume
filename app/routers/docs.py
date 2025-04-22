from fastapi import APIRouter

from app.schemas.docs import DocumentRequest
from app.services.google_auth import load_credentials
from app.services.google_docs import (
    create_document,
    read_document,
    update_document,
)

router = APIRouter(prefix="/docs", tags=["docs"])


@router.post("/read")
async def read_google_doc(request: DocumentRequest):
    """Read content from a Google Doc."""
    credentials = load_credentials(request.user_id)
    document = read_document(credentials, request.document_id)
    return {"document": document}


@router.post("/create")
async def create_google_doc(title: str, user_id: str):
    """Create a new Google Doc."""
    credentials = load_credentials(user_id)
    document = create_document(credentials, title)
    return {"document": document}


@router.post("/update")
async def update_google_doc(document_id: str, content: str, user_id: str):
    """Update content in a Google Doc."""
    credentials = load_credentials(user_id)
    update_document(credentials, document_id, content)
    return {"status": "success"}
