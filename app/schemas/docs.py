from pydantic import BaseModel


class DocumentRequest(BaseModel):
    document_id: str
    user_id: str


class SheetRequest(BaseModel):
    spreadsheet_id: str
    range_name: str
    user_id: str


class JobDescriptionRequest(BaseModel):
    job_description: str
