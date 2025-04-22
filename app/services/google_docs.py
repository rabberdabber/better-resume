from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from fastapi import Depends, HTTPException
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from pydantic import BaseModel

from app.services.google_auth import get_google_credentials
from app.services.resume_generator import (
    CourseworkSection,
    ProjectsSection,
    SkillsSection,
)
from app.utils.language import Language
from app.config.settings import get_template_settings

template_settings = get_template_settings()


class ResumeDocument(BaseModel):
    id: str
    title: str
    url: str


@dataclass
class ResumeData:
    title: str
    professional_summary: str
    experiences: List[str]
    skills: SkillsSection
    projects: ProjectsSection
    coursework: CourseworkSection


def get_docs_service(credentials: Credentials = Depends(get_google_credentials)):
    """Create and return a Google Docs service instance."""
    return build("docs", "v1", credentials=credentials)


def read_document(credentials: Credentials, document_id: str) -> Dict[str, Any]:
    """Read content from a Google Doc."""
    try:
        service = get_docs_service(credentials)
        document = service.documents().get(documentId=document_id).execute()
        return document
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Failed to read document: {str(e)}"
        ) from e


def create_document(
    credentials: Credentials,
    title: str,
    template_id: Optional[str] = None,
) -> Dict[str, Any]:
    """Create a new Google Doc with content, optionally from a template.

    Args:
        credentials: Google OAuth credentials
        title: Title of the new document
        content: Content to insert into the document
        template_id: Optional ID of template document to copy from
    """
    try:
        service = get_docs_service(credentials)
        drive_service = build("drive", "v3", credentials=credentials)

        if template_id:
            # Copy from template using Drive API
            copied_file = (
                drive_service.files()
                .copy(fileId=template_id, body={"name": title})
                .execute()
            )
            return copied_file.get("id")
        else:
            # Create blank document
            document = service.documents().create(body={"title": title}).execute()
            return document.get("documentId")
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Failed to create document: {str(e)}"
        ) from e


def update_document(credentials: Credentials, document_id: str, content: str) -> None:
    """Update content in a Google Doc."""
    try:
        service = get_docs_service(credentials)
        requests = [{"insertText": {"location": {"index": 1}, "text": content}}]
        service.documents().batchUpdate(
            documentId=document_id, body={"requests": requests}
        ).execute()
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Failed to update document: {str(e)}"
        ) from e


class ResumeDocumentBuilder:
    def __init__(self, credentials: Credentials, title: str, language: Language):
        self.credentials = credentials
        self.title = title
        self.template_id = (
            template_settings.TEMPLATE_ID
            if language == "en"
            else template_settings.KOREAN_TEMPLATE_ID
        )
        self.requests = []
        self.service = get_docs_service(credentials)
        self.document_id = create_document(credentials, title, self.template_id)

    def add_professional_summary(self, summary: str) -> "ResumeDocumentBuilder":
        self.requests.append(
            {
                "replaceAllText": {
                    "containsText": {"text": "{{professional_summary_placeholder}}"},
                    "replaceText": summary,
                }
            }
        )
        return self

    def add_experiences(self, experiences: List[str]) -> "ResumeDocumentBuilder":
        for idx, exp in enumerate(experiences, 1):
            self.requests.append(
                {
                    "replaceAllText": {
                        "containsText": {
                            "text": f"{{{{experience_{idx}_placeholder}}}}"
                        },
                        "replaceText": exp,
                    }
                }
            )
        return self

    def add_skills(self, skills: SkillsSection) -> "ResumeDocumentBuilder":
        self.requests.extend(
            [
                {
                    "replaceAllText": {
                        "containsText": {"text": "{{skills_placeholder}}"},
                        "replaceText": skills.comma_separated_text,
                    }
                },
                {
                    "replaceAllText": {
                        "containsText": {"text": "{{skills_summary_placeholder}}"},
                        "replaceText": skills.summary_text,
                    }
                },
            ]
        )
        return self

    def add_projects(self, projects: ProjectsSection) -> "ResumeDocumentBuilder":
        if len(projects.projects) >= 2:
            project_a = projects.projects[0]
            project_b = projects.projects[1]

            project_requests = [
                # Project A
                {
                    "replaceAllText": {
                        "containsText": {"text": "{{project_one_name_placeholder}}"},
                        "replaceText": project_a.name,
                    }
                },
                {
                    "replaceAllText": {
                        "containsText": {"text": "{{project_one_link_placeholder}}"},
                        "replaceText": f"({project_a.url})",
                    }
                },
                {
                    "replaceAllText": {
                        "containsText": {
                            "text": "{{project_one_duration_placeholder}}"
                        },
                        "replaceText": project_a.date,
                    }
                },
                {
                    "replaceAllText": {
                        "containsText": {"text": "{{project_one_1_placeholder}}"},
                        "replaceText": project_a.formatted_bullets[0],
                    }
                },
                {
                    "replaceAllText": {
                        "containsText": {"text": "{{project_one_2_placeholder}}"},
                        "replaceText": project_a.formatted_bullets[1],
                    }
                },
                # Project B
                {
                    "replaceAllText": {
                        "containsText": {"text": "{{project_two_name_placeholder}}"},
                        "replaceText": project_b.name,
                    }
                },
                {
                    "replaceAllText": {
                        "containsText": {"text": "{{project_two_link_placeholder}}"},
                        "replaceText": f"({project_b.url})",
                    }
                },
                {
                    "replaceAllText": {
                        "containsText": {
                            "text": "{{project_two_duration_placeholder}}"
                        },
                        "replaceText": project_b.date,
                    }
                },
                {
                    "replaceAllText": {
                        "containsText": {"text": "{{project_two_1_placeholder}}"},
                        "replaceText": project_b.formatted_bullets[0],
                    }
                },
                {
                    "replaceAllText": {
                        "containsText": {"text": "{{project_two_2_placeholder}}"},
                        "replaceText": project_b.formatted_bullets[1],
                    }
                },
            ]

            # Add all requests at once
            self.requests.extend(project_requests)

        return self

    def add_coursework(self, coursework: CourseworkSection) -> "ResumeDocumentBuilder":
        self.requests.append(
            {
                "replaceAllText": {
                    "containsText": {"text": "{{coursework_placeholder}}"},
                    "replaceText": coursework.comma_separated_text,
                }
            }
        )
        return self

    def build(self) -> ResumeDocument:
        try:
            self.service.documents().batchUpdate(
                documentId=self.document_id, body={"requests": self.requests}
            ).execute()

            return ResumeDocument(
                id=self.document_id,
                title=self.title,
                url=f"https://docs.google.com/document/d/{self.document_id}/edit",
            )
        except Exception as e:
            raise HTTPException(
                status_code=400, detail=f"Failed to create resume document: {str(e)}"
            ) from e


def create_resume_document(
    credentials: Credentials, resume_data: ResumeData, language: Language
) -> ResumeDocument:
    """Create a new Google Doc with resume content, optionally from a template."""
    return (
        ResumeDocumentBuilder(credentials, resume_data.title, language)
        .add_professional_summary(resume_data.professional_summary)
        .add_experiences(resume_data.experiences)
        .add_skills(resume_data.skills)
        .add_projects(resume_data.projects)
        .add_coursework(resume_data.coursework)
        .build()
    )
