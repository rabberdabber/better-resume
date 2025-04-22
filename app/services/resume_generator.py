from typing import Dict

from pydantic import BaseModel

from app.services.gemini_client import client
from app.utils.language import get_language_name


class ExperienceBullet(BaseModel):
    what: str
    how: str
    impact: str
    tech_stack: list[str]
    formatted_text: str


class ProfessionalSummary(BaseModel):
    summary: str


class SkillsSection(BaseModel):
    relevant_tools: list[str]
    summary_text: str
    comma_separated_text: str


class CourseworkSection(BaseModel):
    selected_coursework: list[str]
    comma_separated_text: str


class Project(BaseModel):
    name: str
    url: str
    date: str
    tech_stack: list[str]
    formatted_bullets: list[str]


class ProjectsSection(BaseModel):
    projects: list[Project]


class ResumeContent(BaseModel):
    professional_summary: ProfessionalSummary
    selected_experiences: list[ExperienceBullet]
    skills: SkillsSection
    projects: ProjectsSection
    coursework: CourseworkSection


class ResumeContentBuilder:
    # Class constants for configuration
    MAX_EXPERIENCE_BULLET_WORDS = 150
    MAX_PROJECT_BULLET_WORDS = 150
    MAX_PROJECTS = 2
    MAX_COURSEWORK = 5
    MAX_SUMMARY_SENTENCES = 2
    MAX_EXPERIENCE_BULLETS = 4

    def __init__(self, job_description: str, resume_data: Dict, language: str):
        self.job_description = job_description
        self.resume_data = resume_data
        self.language = language
        self.language_name = get_language_name(language)
        self.professional_summary = None
        self.selected_experiences = None
        self.skills = None
        self.projects = None
        self.coursework = None
        self.max_summary_sentences = (
            self.MAX_SUMMARY_SENTENCES + 1
            if language == "kr"
            else self.MAX_SUMMARY_SENTENCES
        )

    def build_professional_summary(self) -> "ResumeContentBuilder":
        summary_prompt = f"""
        Based on this resume data and job description, generate a professional summary in
        {self.max_summary_sentences} sentences in {self.language_name}
        that highlights key achievements and skills:

        Resume Data:
        {self.resume_data}

        Job Description:
        {self.job_description}

        Focus on:
        1. Relevant technical skills and experience
        2. Quantifiable achievements
        3. Alignment with job requirements

        Format the response as JSON with this structure:
        {{"summary": "your generated summary"}}
        """

        summary_response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=summary_prompt,
            config={
                "response_mime_type": "application/json",
                "response_schema": ProfessionalSummary,
            },
        )

        self.professional_summary = summary_response.parsed
        return self

    def build_skills(self) -> "ResumeContentBuilder":
        skills_prompt = f"""
        Based on this resume data and job description, select the most relevant tools, frameworks, and technologies:

        Resume Data:
        Tools & Frameworks: {self.resume_data["skills"]["tools_os_frameworks"]}

        Job Description:
        {self.job_description}

        Create a curated list of relevant tools and technologies. Format as JSON with this structure:
        {{
            "relevant_tools": ["tool1", "tool2", "tool3"],
            "summary_text": "Experienced with AWS, Docker, and Kubernetes for cloud deployment. Proficient in CI/CD with Github Actions and security practices including OAuth 2.0 and JWT.",
            "comma_separated_text": "AWS, Docker, Kubernetes, Github Actions, OAuth 2.0, JWT, FastAPI, PostgreSQL"
        }}

        Focus on:
        1. Tools and technologies specifically mentioned in the job description
        2. Related or complementary tools from the resume
        3. For summary_text: Create natural-sounding paragraphs grouped by capability
        4. For comma_separated_text: List most important tools separated by commas
        5. Ensure both formats cover key technical capabilities
        """

        skills_response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=skills_prompt,
            config={
                "response_mime_type": "application/json",
                "response_schema": SkillsSection,
            },
        )

        self.skills = skills_response.parsed
        return self

    def build_experiences(self) -> "ResumeContentBuilder":
        experiences_prompt = f"""
        Based on this resume data and job description, select and format the top {self.MAX_EXPERIENCE_BULLETS} most relevant experiences in {self.language_name}:

        Resume Data:
        {self.resume_data["experience"]}

        Job Description:
        {self.job_description}

        For each experience:
        1. Keep the structured data (what/how/impact/tech_stack)
        2. Create a formatted_text field that combines these elements into a compelling, professional bullet point with no more than {self.MAX_EXPERIENCE_BULLET_WORDS} words
        3. Ensure the formatted text:
           - Uses strong action verbs
           - Emphasizes quantifiable achievements
           - Highlights relevant technical skills
           - Maintains professional tone
           - Focuses on impact and results
        4. Prioritize experiences most relevant to the job description

        Format as a JSON list where each experience includes all fields plus a formatted_text field.

        Example structure:
        {{
            "what": "Developed backend system",
            "how": "Implemented microservices architecture",
            "impact": "Reduced latency by 50%",
            "tech_stack": ["FastAPI", "Docker"],
            "formatted_text": "Engineered high-performance microservices backend using FastAPI and Docker, reducing system latency by 50% while ensuring ISO 27001 compliance"
        }}
        """

        experiences_response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=experiences_prompt,
            config={
                "response_mime_type": "application/json",
                "response_schema": list[ExperienceBullet],
            },
        )

        self.selected_experiences = experiences_response.parsed
        return self

    def build_projects(self) -> "ResumeContentBuilder":
        projects_prompt = f"""
        Based on this resume data and job description, select and format the {self.MAX_PROJECTS} most relevant projects in {self.language_name}:

        Resume Data:
        {self.resume_data["projects"]}

        Job Description:
        {self.job_description}

        For each project:
        1. Select the most relevant bullets based on the job description
        2. Create two formatted bullet points that:
           - Use strong action verbs
           - Emphasize technical achievements
           - Highlight relevant technologies
           - Focus on impact and results
           - Keep each bullet under {self.MAX_PROJECT_BULLET_WORDS} words
        3. Order the projects by relevance to the job description

        Format as JSON with this structure:
        {{
            "projects": [
                {{
                    "name": "Project Name",
                    "url": "project url",
                    "date": "date range",
                    "tech_stack": ["tech1", "tech2"],
                    "formatted_bullets": [
                        "First formatted bullet point",
                        "Second formatted bullet point"
                    ]
                }}
            ]
        }}
        """

        projects_response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=projects_prompt,
            config={
                "response_mime_type": "application/json",
                "response_schema": ProjectsSection,
            },
        )

        self.projects = projects_response.parsed
        return self

    def build_coursework(self) -> "ResumeContentBuilder":
        coursework_prefix = (
            "관련 수강과목:" if self.language == "kr" else "Relevant Coursework:"
        )
        coursework_prompt = f"""
        Based on this resume data and job description, select the top {self.MAX_COURSEWORK} most relevant coursework in {self.language_name}:

        Resume Data:
        Coursework: {self.resume_data["coursework"]["list"]}

        Job Description:
        {self.job_description}

        Select coursework that:
        1. Directly relates to the job requirements
        2. Demonstrates relevant technical knowledge
        3. Shows depth in required areas
        4. Complements the professional experience

        Format as JSON with this structure:
        {{
            "selected_coursework": [
                "Course 1",
                "Course 2",
                "Course 3",
                "Course 4",
                "Course 5"
            ],
            "comma_separated_text": "{coursework_prefix} Course 1, Course 2, Course 3, Course 4, Course 5"
        }}

        Important:
        1. Return the coursework in {self.language_name}
        2. If the language is Korean:
           - Translate the course names to Korean
           - Include the original English course name in parentheses
           - Example: "데이터베이스 시스템 (Database Systems)"
        3. Maintain the same meaning and technical accuracy in translation
        4. Keep the comma-separated text in the same format with both languages when Korean
        5. The comma-separated text should start with "{coursework_prefix}"
        """

        coursework_response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=coursework_prompt,
            config={
                "response_mime_type": "application/json",
                "response_schema": CourseworkSection,
            },
        )

        self.coursework = coursework_response.parsed
        return self

    def build(self) -> ResumeContent:
        return ResumeContent(
            professional_summary=self.professional_summary,
            selected_experiences=self.selected_experiences,
            skills=self.skills,
            projects=self.projects,
            coursework=self.coursework,
        )


def generate_resume(
    job_description: str, resume_data: Dict, language: str
) -> ResumeContent:
    """
    Generate tailored resume content using Gemini AI based on job description.

    Args:
        job_description (str): The job description to tailor the resume for
        resume_data (Dict): The base resume data from TOML config
        language (str): The language to generate the resume in ("en" or "ko")

    Returns:
        ResumeContent: Generated resume content with formatted experiences
    """
    return (
        ResumeContentBuilder(job_description, resume_data, language)
        .build_professional_summary()
        .build_skills()
        .build_experiences()
        .build_projects()
        .build_coursework()
        .build()
    )
