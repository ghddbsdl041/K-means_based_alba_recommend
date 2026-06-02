# Work24 (고용24) API Integration Gateway

An asynchronous FastAPI backend proxy service that securely connects with Korean Work24 (고용24 / 워크넷) OpenAPI endpoints. It aggregates Recruitment (채용정보), Job Duty (직무정보), and Occupation (직업정보) data while shielding access credentials from frontend clients.

## Project Structure

```text
work24-backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # Application setup, CORS, and initialization
│   ├── config.py            # Pydantic Settings configuration validator
│   ├── core/
│   │   ├── __init__.py
│   │   └── utils.py         # XML-to-JSON parsing & dictionary sanitization utilities
│   ├── services/
│   │   ├── __init__.py
│   │   ├── recruitment.py   # Asynchronous client for wantedApi.do
│   │   ├── occupation.py    # Asynchronous client for jobSrch.do
│   │   └── duty.py          # Asynchronous client for NCS / Duty APIs
│   └── routers/
│       ├── __init__.py
│       ├── recruitment.py   # Routers for /api/recruitment
│       ├── occupation.py    # Routers for /api/occupations
│       └── duty.py          # Routers for /api/duties
├── .env                     # Local environment keys (ignored from git)
├── .env.example             # Template for variables setup
├── requirements.txt         # Required python package list
└── README.md
```

## Setup & Running Instructions

### 1. Prerequisite
Ensure Python 3.9+ is installed.

### 2. Install Dependencies
Initialize a virtual environment and install the required modules:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Setup Variables
Verify that the `.env` file in the root directory contains your actual credentials:
```env
WORK24_RECRUIT_API_KEY=347fbf3a-87d7-487c-9d9b-c38a7dc53df7
WORK24_DUTY_API_KEY=9fe9f129-3f79-4fc6-8edd-afa01122b76e
WORK24_OCCUPATION_API_KEY=69ee267f-48d4-4677-9f0c-98c31b0b7c3b
```

### 4. Run Server
Start the development server:
```bash
uvicorn app.main:app --reload --port 8000
```
Or run `python app/main.py`.

## API Endpoints Overview

Open [http://localhost:8000/docs](http://localhost:8000/docs) in your browser to view the interactive Swagger UI and test endpoints directly.

### Recruitment API
- **`GET /api/recruitment/jobs`**: Fetch and filter active job listings.
- **`GET /api/recruitment/jobs/{wanted_auth_no}`**: Fetch comprehensive description of a specific job listing.

### Occupation API
- **`GET /api/occupations/search`**: Search career indexes, classifications, and titles.
- **`GET /api/occupations/detail`**: Fetch comprehensive salary details, descriptions, and guide statistics for a specific occupational code.

### Duties (NCS) API
- **`GET /api/duties/search`**: Search National Competency Standards (NCS) capability elements and tasks.
