from pydantic import BaseModel


class OAuthCallbackRequest(BaseModel):
    code: str
    user_id: str
