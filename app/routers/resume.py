from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Query
from google.oauth2.credentials import Credentials

from app.config.settings import get_settings, get_template_settings
from app.services.google_auth import get_google_credentials
from app.services.google_docs import ResumeData, create_resume_document
from app.services.resume_generator import generate_resume
from app.services.toml_loader import load_resume_data
from app.utils.language import Language, get_language_name

router = APIRouter(prefix="/resume", tags=["resume"])
settings = get_settings()
template_settings = get_template_settings()

# Path to the resume data TOML file
RESUME_DATA_PATH = Path("app/config/resume_data.toml")


@router.post("/generate-with-ai")
def generate_resume_with_ai(
    job_description: str,
    language: Language = Query(default="en"),
    credentials: Credentials = Depends(get_google_credentials),
) -> dict:
    """
    Generate an AI-tailored resume using the TOML data and Gemini AI,
    then create a Google Doc with the content
    """
    try:
        resume_data = load_resume_data(RESUME_DATA_PATH)

        tailored_content = generate_resume(job_description, resume_data, language)
        print(tailored_content)

        doc_title = (
            f"{get_language_name(language)} Resume - {resume_data['personal']['name']}"
        )
        resume_data = ResumeData(
            title=doc_title,
            professional_summary=tailored_content.professional_summary.summary,
            experiences=[
                exp.formatted_text for exp in tailored_content.selected_experiences
            ],
            skills=tailored_content.skills,
            projects=tailored_content.projects,
            coursework=tailored_content.coursework,
        )

        document = create_resume_document(
            credentials=credentials, resume_data=resume_data, language=language
        )
        document_id = document.id
        return {
            "message": "Resume created successfully",
            "document": {
                "id": document_id,
                "title": doc_title,
                "url": f"https://docs.google.com/document/d/{document_id}/edit",
            },
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
