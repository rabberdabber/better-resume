# Resume Assistant

An AI-powered resume and cover letter assistant that helps tailor your resume to specific job descriptions using Gemini AI.

## Features

- FastAPI backend for resume generation
- TOML-based resume data configuration
- Gemini AI integration for intelligent content tailoring
- RESTful API endpoints for easy integration

## Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd resume-assistant
```

2. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -e .
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env and add your Gemini API key
GEMINI_API_KEY=your_api_key_here
```

5. Start the server:
```bash
uvicorn main:app --reload
```

## Usage

1. Edit the `config/resume_data.toml` file with your resume information.

2. Make a POST request to `/generate-resume` with a job description:
```bash
curl -X POST "http://localhost:8000/generate-resume" \
     -H "Content-Type: application/json" \
     -d '{"job_description": "Your job description here"}'
```

3. The API will return tailored resume content based on the job description.

## API Endpoints

- `POST /generate-resume`: Generate tailored resume content
- `GET /health`: Health check endpoint

## Configuration

The `config/resume_data.toml` file contains your base resume information. Update it with your:
- Personal information
- Work experience
- Skills
- Education
- Certifications

## License

MIT
