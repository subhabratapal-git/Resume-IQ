# ResumeIQ — Full-Stack Resume Analysis & Job Matching Platform

ResumeIQ is a **full-stack resume analysis and job-matching platform** designed to help users understand the strengths and weaknesses of their resumes and improve them for specific job opportunities.

The application combines **rule-based analysis, machine learning, natural language processing, document processing, authentication, job-description matching, generative AI, and PDF report generation** into a single platform.

ResumeIQ provides two different analysis modes:

- **Normal Mode** — Rule-based resume analysis
- **Pro Mode** — Machine-learning-based analysis with AI-powered recommendations

The main goal of ResumeIQ is not only to provide a resume score, but also to explain **what needs improvement, why it needs improvement, and how the user can improve it**.

---

## Table of Contents

- [Project Overview](#project-overview)
- [Problem Statement](#problem-statement)
- [Project Objectives](#project-objectives)
- [Key Features](#key-features)
- [Normal Mode](#normal-mode)
- [Pro Mode](#pro-mode)
- [Normal Mode vs Pro Mode](#normal-mode-vs-pro-mode)
- [Resume Analysis Workflow](#resume-analysis-workflow)
- [Rule-Based Analysis](#rule-based-analysis)
- [Machine Learning Analysis](#machine-learning-analysis)
- [AI-Powered Recommendations](#ai-powered-recommendations)
- [PDF Improvement Report](#pdf-improvement-report)
- [Job Description Matching](#job-description-matching)
- [Authentication](#authentication)
- [Analysis History](#analysis-history)
- [Full-Stack Architecture](#full-stack-architecture)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Backend Services](#backend-services)
- [Frontend Structure](#frontend-structure)
- [API Overview](#api-overview)
- [Database](#database)
- [Environment Variables](#environment-variables)
- [Local Development Setup](#local-development-setup)
- [Running the Application](#running-the-application)
- [Production Build](#production-build)
- [Deployment Architecture](#deployment-architecture)
- [Security](#security)
- [Testing](#testing)
- [Current Limitations](#current-limitations)
- [Future Improvements](#future-improvements)
- [Project Goals](#project-goals)
- [Conclusion](#conclusion)

---

# Project Overview

ResumeIQ is a full-stack web application that analyzes resumes and provides structured feedback to users.

The application consists of:

- React frontend
- FastAPI backend
- Database layer
- Rule-based analysis engine
- Machine learning analysis engine
- Gemini AI integration
- PDF report generation
- Authentication system

A typical workflow is:

```text
User
  ↓
Upload Resume
  ↓
Resume Text Extraction
  ↓
Text Cleaning
  ↓
Section Detection
  ↓
Analysis
  ↓
Normal Mode / Pro Mode
  ↓
Scores + Feedback
  ↓
Improvement Recommendations
  ↓
PDF Report
```

---

# Problem Statement

Many candidates submit resumes without knowing whether their resume is properly structured or relevant to the job they are applying for.

Common problems include:

- Missing resume sections
- Weak resume structure
- Missing job-related keywords
- Irrelevant skills
- Weak project descriptions
- Poor presentation of experience
- Low job-description relevance
- Lack of actionable improvement guidance

A simple resume score is often not enough.

Users need to understand:

> What is wrong?

> Why is it a problem?

> Which part should be improved?

> How should it be improved?

ResumeIQ attempts to solve this problem through a combination of rule-based analysis, machine learning, and AI-powered recommendations.

---

# Project Objectives

The major objectives of ResumeIQ are:

- Analyze resumes automatically.
- Extract text from PDF and DOCX resumes.
- Clean and preprocess extracted text.
- Detect important resume sections.
- Evaluate resume structure.
- Analyze skills and keywords.
- Evaluate education, experience, and projects.
- Compare resumes with job descriptions.
- Perform ML-based semantic matching.
- Identify strong and weak areas.
- Provide actionable improvement recommendations.
- Generate structured PDF improvement reports.
- Maintain user authentication.
- Store user-specific analysis information.
- Provide a complete full-stack application architecture.

---

# Key Features

## Resume Upload

Users can upload resumes in supported document formats such as:

- PDF
- DOCX

---

## Resume Text Extraction

The backend extracts text from uploaded documents using document-processing libraries.

---

## Resume Section Detection

The system identifies important sections such as:

- Summary
- Skills
- Education
- Experience
- Projects
- Certifications
- Other relevant sections

---

## ATS-Oriented Analysis

ResumeIQ evaluates several resume factors related to ATS compatibility and resume structure.

---

## Skill Extraction

The system extracts skills from resume content and evaluates their relevance.

---

## Keyword Matching

Resume keywords can be compared with job-description keywords to identify relevant and potentially missing terms.

---

## Experience Analysis

The experience section is evaluated as part of the overall resume analysis.

---

## Education Analysis

Education-related resume information is included in the analysis.

---

## Project Analysis

Technical projects are analyzed as an important part of the resume, especially for technical roles.

---

## Error Detection

Potential resume issues and weaknesses can be identified through the analysis system.

---

## Job Matching

The resume can be compared against a target job description to understand job relevance.

---

## AI-Powered Recommendations

Pro Mode can use the Gemini API to provide more detailed recommendations about improving the resume.

---

## PDF Improvement Report

Pro Mode can generate a structured PDF report containing improvement guidance and analysis results.

---

# Normal Mode

## Rule-Based Resume Analysis

Normal Mode is the standard resume analysis system of ResumeIQ.

It uses **rule-based logic and predefined scoring methods** rather than ML-based semantic analysis.

The Normal Mode analysis focuses on areas such as:

- Resume structure
- Section detection
- ATS-related factors
- Keywords
- Skills
- Education
- Experience
- Projects
- Errors
- Job-description relevance

The simplified workflow is:

```text
Resume
   ↓
Text Extraction
   ↓
Text Cleaning
   ↓
Section Detection
   ↓
Rule-Based Analysis
   ↓
Scoring
   ↓
Feedback
```

### Advantages

- Fast analysis
- Lightweight
- Suitable for general resume evaluation
- Does not require advanced semantic ML processing
- Available as the standard analysis mode

---

# Pro Mode

## Machine Learning-Based Resume Analysis

Pro Mode provides a more advanced analysis pipeline.

The current ML implementation uses:

- **TF-IDF Vectorization**
- **Cosine Similarity**
- Resume-to-job-description semantic comparison
- Section-level similarity analysis

The simplified workflow is:

```text
Resume
   +
Job Description
   ↓
Text Processing
   ↓
TF-IDF Vectorization
   ↓
Vector Representation
   ↓
Cosine Similarity
   ↓
Semantic Score
   ↓
Strong / Weak Areas
   ↓
AI Recommendations
   ↓
PDF Improvement Report
```

---

# Pro Mode Free Usage

Pro Mode follows a limited free-usage model.

Each user can perform:

**5 Pro analyses for free.**

After the five free analyses are used, the user needs a subscription to continue using Pro Mode.

The project currently contains the subscription/premium interface and access flow.

### Payment Status

A real payment gateway has **not yet been implemented**.

The current project therefore represents the subscription experience at the application level.

A real payment provider can be integrated in a future version.

---

# Normal Mode vs Pro Mode

| Feature | Normal Mode | Pro Mode |
|---|---|---|
| Analysis Type | Rule-Based | ML-Based |
| Resume Parsing | Yes | Yes |
| Text Cleaning | Yes | Yes |
| Section Detection | Yes | Yes |
| ATS Analysis | Yes | Yes |
| Keyword Analysis | Yes | Yes |
| Skill Analysis | Yes | Yes |
| Education Analysis | Yes | Yes |
| Experience Analysis | Yes | Yes |
| Project Analysis | Yes | Yes |
| Error Detection | Yes | Yes |
| Job Matching | Yes | Yes |
| TF-IDF | No | Yes |
| Cosine Similarity | No | Yes |
| Semantic Matching | No | Yes |
| Strong / Weak Semantic Areas | No | Yes |
| AI Recommendations | No | Yes |
| Improvement Guidance | Basic | Detailed |
| PDF Improvement Report | No | Yes |
| Free Pro Usage | Not applicable | 5 analyses |
| Subscription Required | No | After free limit |
| Real Payment Gateway | Not applicable | Not implemented |

---

# Resume Analysis Workflow

The complete analysis pipeline can be represented as:

```text
                    User
                      │
                      ▼
              React Frontend
                      │
                      │ REST API
                      ▼
              FastAPI Backend
                      │
          ┌───────────┼───────────┐
          │           │           │
          ▼           ▼           ▼
     Authentication  Resume    Job Description
                     Parser
                       │
                       ▼
                  Text Cleaning
                       │
                       ▼
                 Section Detection
                       │
                       ▼
                 Analysis Engine
                       │
              ┌────────┴────────┐
              │                 │
              ▼                 ▼
        Normal Mode         Pro Mode
        Rule-Based          ML-Based
              │                 │
              │                 ▼
              │          Semantic Matching
              │                 │
              │                 ▼
              │          AI Recommendations
              │                 │
              │                 ▼
              │            PDF Report
              │                 │
              └────────┬────────┘
                       │
                       ▼
                    Database
```

---

# How Resume Analysis Works

## Step 1 — Resume Upload

The user uploads a supported resume document.

---

## Step 2 — Text Extraction

The backend extracts readable text from the document.

Libraries used include:

- `pypdf`
- `python-docx`

---

## Step 3 — Text Cleaning

Extracted text is cleaned and prepared for further processing.

This helps reduce formatting-related artifacts and creates cleaner input for the analysis modules.

---

## Step 4 — Section Detection

The system identifies important resume sections.

The detected sections are then passed to different analysis components.

---

## Step 5 — Resume Feature Analysis

Different services analyze different parts of the resume.

```text
Resume
 ├── Structure
 ├── Skills
 ├── Keywords
 ├── Education
 ├── Experience
 ├── Projects
 └── Errors
```

---

## Step 6 — Analysis Mode

The selected analysis mode determines the next stage.

### Normal Mode

```text
Rules
  ↓
Scores
  ↓
Feedback
```

### Pro Mode

```text
ML Semantic Analysis
        ↓
Strong / Weak Areas
        ↓
AI Recommendations
        ↓
PDF Improvement Report
```

---

# Rule-Based Analysis

The rule-based analysis system uses predefined conditions and scoring logic.

The analysis has been divided into multiple backend services to keep the architecture modular.

Major components include:

- ATS scoring
- Structure scoring
- Education scoring
- Experience scoring
- Project scoring
- Keyword matching
- Skill extraction
- Error detection
- Job matching

This modular approach makes individual analysis components easier to maintain and improve.

---

# Machine Learning Analysis

The current Pro Mode semantic analysis uses **Scikit-learn**.

## TF-IDF

TF-IDF stands for:

**Term Frequency — Inverse Document Frequency**

It converts text into numerical vectors based on the importance of words in the provided documents.

ResumeIQ uses text from:

- Resume
- Job description
- Relevant resume sections

to generate vector representations.

---

## Cosine Similarity

Cosine similarity measures the similarity between two vector representations.

Conceptually:

```text
Resume Vector
      │
      ▼
Cosine Similarity
      ▲
      │
Job Description Vector
```

The similarity result is converted into a percentage-style semantic score.

---

## Section-Level Semantic Analysis

Pro Mode can also compare individual resume sections against the job description.

Example:

```text
Skills       → High Match
Experience   → High Match
Projects     → Low Match
Education    → Moderate Match
```

This allows the user to understand which areas of the resume are stronger or weaker in relation to the target job.

---

# AI-Powered Recommendations

Pro Mode can use the Google Gemini API to provide more detailed recommendations.

The AI layer is intended to convert analysis results into actionable suggestions.

For example, instead of only showing:

```text
Projects Section: Low Match
```

the system can provide guidance such as:

```text
The projects section has limited alignment with the target role.

Recommended improvements:

- Highlight technologies relevant to the job description.
- Explain the candidate's contribution to each project.
- Include measurable outcomes where appropriate.
- Prioritize projects that demonstrate relevant skills.
```

The recommendations depend on the resume and job description provided by the user.

---

# PDF Improvement Report

Pro Mode can generate a structured PDF report to help the user improve the resume.

The report can contain information such as:

```text
Resume Improvement Report
│
├── Overall Analysis
│
├── Resume Score
│
├── Job Match Summary
│
├── Strong Areas
│
├── Weak Areas
│
├── Keyword Recommendations
│
├── Skill Recommendations
│
├── Experience Improvements
│
├── Project Improvements
│
├── Education Improvements
│
├── Structure / ATS Recommendations
│
└── Recommended Next Steps
```

The main purpose of the report is to answer:

> **What should I change and how should I improve my resume?**

---

# Job Description Matching

ResumeIQ can compare a resume against a target Job Description (JD).

The matching process can consider:

- Keywords
- Skills
- Resume sections
- Experience
- Projects
- Semantic similarity

Conceptually:

```text
                Resume
                  │
       ┌──────────┼──────────┐
       ▼          ▼          ▼
     Skills   Experience   Projects
       │          │          │
       └──────────┼──────────┘
                  │
                  ▼
              Comparison
                  ▲
                  │
          Job Description
```

The result helps users understand how closely their resume aligns with the target position.

---

# Authentication

ResumeIQ includes a backend authentication system.

The authentication architecture includes:

- User registration
- User login
- Password hashing
- JWT authentication
- Protected routes
- User-specific analysis information

Authentication logic is separated from the API route layer.

---

# Analysis History

Authenticated users can have analysis records associated with their accounts.

This allows the application to support:

- Previous analysis records
- User-specific analysis history
- Analysis tracking
- Repeated resume evaluation

The backend database layer manages these records.

---

# Full-Stack Architecture

ResumeIQ is a complete full-stack application.

## Frontend

The frontend is responsible for:

- User interface
- Authentication screens
- Dashboard
- Resume upload
- Analysis display
- Normal Mode
- Pro Mode
- Subscription interface
- Profile interface
- Theme controls
- API communication

---

## Backend

The backend is responsible for:

- Authentication
- Resume processing
- Text extraction
- Text cleaning
- Section detection
- Rule-based analysis
- ML-based analysis
- Job matching
- AI integration
- PDF generation
- Database operations
- REST APIs

---

## Database

The database layer stores application data such as:

- Users
- Resume analysis records
- Analysis-related information

---

# Technology Stack

## Frontend

| Technology | Purpose |
|---|---|
| React.js | User interface |
| Vite | Frontend build tool |
| React Router | Client-side routing |
| Axios | HTTP/API communication |
| JavaScript | Application logic |
| CSS | Styling |

---

## Backend

| Technology | Purpose |
|---|---|
| Python | Backend programming |
| FastAPI | REST API framework |
| Uvicorn | ASGI server |
| SQLAlchemy | ORM / database interaction |
| Pydantic | Data validation |
| PyJWT | JWT authentication |
| Argon2 | Password hashing |
| python-dotenv | Environment configuration |

---

## Document Processing

| Library | Purpose |
|---|---|
| pypdf | PDF text extraction |
| python-docx | DOCX processing |
| fpdf2 | PDF report generation |

---

## Machine Learning

| Technology | Purpose |
|---|---|
| Scikit-learn | Machine learning utilities |
| TF-IDF | Text vectorization |
| Cosine Similarity | Semantic similarity |

---

## Generative AI

| Technology | Purpose |
|---|---|
| Google Gemini API | AI-powered recommendations and analysis assistance |

---

# Project Structure

```text
ResumeIQ/
│
├── backend/
│   │
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── database.py
│   │   │
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── analysis.py
│   │   │   └── user.py
│   │   │
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py
│   │   │   ├── resume.py
│   │   │   └── pro.py
│   │   │
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   └── user.py
│   │   │
│   │   └── services/
│   │       ├── __init__.py
│   │       ├── ai_service.py
│   │       ├── ats_scorer.py
│   │       ├── auth_service.py
│   │       ├── document_generator.py
│   │       ├── education_scorer.py
│   │       ├── error_detector.py
│   │       ├── experience_scorer.py
│   │       ├── job_matcher.py
│   │       ├── keyword_matcher.py
│   │       ├── ml_scorer.py
│   │       ├── project_scorer.py
│   │       ├── resume_parser.py
│   │       ├── section_detector.py
│   │       ├── skill_extractor.py
│   │       ├── structure_scorer.py
│   │       └── text_cleaner.py
│   │
│   ├── tests/
│   │   └── test_analysis_history.py
│   │
│   ├── requirements.txt
│   └── sample_resume.pdf
│
├── database/
│   └── resumeiq.db          # Local runtime database, not committed
│
├── frontend/
│   │
│   ├── src/
│   │   ├── components/
│   │   ├── data/
│   │   ├── pages/
│   │   ├── services/
│   │   ├── styles/
│   │   ├── App.jsx
│   │   ├── config.js
│   │   └── main.jsx
│   │
│   ├── index.html
│   ├── package.json
│   ├── package-lock.json
│   ├── eslint.config.js
│   └── vite.config.js
│
├── .gitignore
└── README.md
```

---

# Backend Services

The backend follows a modular architecture.

## `resume_parser.py`

Extracts text from supported resume documents.

---

## `text_cleaner.py`

Cleans and prepares extracted resume text.

---

## `section_detector.py`

Detects and organizes resume sections.

---

## `ats_scorer.py`

Performs ATS-oriented resume evaluation.

---

## `keyword_matcher.py`

Compares relevant keywords between resume and job description.

---

## `skill_extractor.py`

Extracts relevant skills from resume content.

---

## `education_scorer.py`

Evaluates education-related information.

---

## `experience_scorer.py`

Evaluates experience-related resume information.

---

## `project_scorer.py`

Evaluates project-related resume content.

---

## `structure_scorer.py`

Evaluates structural aspects of the resume.

---

## `error_detector.py`

Identifies potential resume errors and weaknesses.

---

## `job_matcher.py`

Handles job-description matching logic.

---

## `ml_scorer.py`

Performs machine-learning-based semantic scoring using:

- TF-IDF
- Cosine similarity

It can produce:

- Overall semantic score
- Strong areas
- Weak areas

---

## `ai_service.py`

Handles communication with the Google Gemini API.

The Gemini API key is kept on the backend and loaded through environment configuration.

---

## `document_generator.py`

Generates structured PDF improvement reports.

---

# Frontend Structure

The React frontend is organized into reusable components, pages, services, and styles.

## Components

Examples include:

- `Brand`
- `ModeCard`
- `ProfileMenu`
- `ProtectedRoute`
- `ResumeAnalyzer`
- `ResumeArtwork`
- `ScoreCard`
- `ThemeToggle`

---

## Pages

The application contains pages such as:

- Login
- Dashboard
- Pro Dashboard

---

## API Services

Frontend API communication is separated into service modules.

Examples include:

- Authentication API
- Resume API

This keeps API communication separate from UI components.

---

# API Overview

The backend is implemented using FastAPI.

Major API areas include:

```text
/auth
/resume
/api/pro
```

The application also provides health and statistics endpoints.

## Health Check

```http
GET /health
```

Example response:

```json
{
  "status": "ok",
  "service": "ResumeIQ API"
}
```

## Root Endpoint

```http
GET /
```

Example response:

```json
{
  "message": "ResumeIQ API is running"
}
```

API documentation can be enabled during development/testing through backend configuration.

---

# Database

ResumeIQ currently uses **SQLite** through SQLAlchemy.

The database is used by the backend to store application data such as users and analysis records.

The local database file is intentionally excluded from Git:

```gitignore
database/*.db
```

This prevents local user data and database contents from being committed to GitHub.

For a production deployment requiring stronger persistence and scalability, the database layer can later be migrated to a managed relational database such as PostgreSQL.

---

# Environment Variables

Sensitive configuration must never be hardcoded into source code.

Example backend environment configuration:

```env
GEMINI_API_KEY=your_gemini_api_key
JWT_SECRET_KEY=your_secret_key
ENABLE_DOCS=false
```

These values are examples only.

**Never commit real credentials to GitHub.**

The `.env` file is excluded using `.gitignore`.

---

# Frontend API Configuration

The frontend uses the following environment variable:

```text
VITE_API_URL
```

The API configuration is centralized in:

```text
frontend/src/config.js
```

### Development

```env
VITE_API_URL=http://127.0.0.1:8000
```

### Production

```env
VITE_API_URL=https://your-backend-domain.onrender.com
```

Only the backend API URL should be exposed to the frontend.

The Gemini API key must remain on the backend.

---

# Local Development Setup

## Prerequisites

Install:

- Python 3.11+
- Node.js
- npm
- Git

---

# Backend Setup

Navigate to the backend directory:

```bash
cd backend
```

Create a virtual environment:

```bash
python -m venv venv
```

Activate it on Windows:

```powershell
.\venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create a backend `.env` file:

```env
GEMINI_API_KEY=your_gemini_api_key
JWT_SECRET_KEY=your_secret_key
```

Start the backend:

```bash
uvicorn app.main:app --reload
```

The backend normally runs at:

```text
http://127.0.0.1:8000
```

---

# Frontend Setup

Open another terminal.

Navigate to:

```bash
cd frontend
```

Install dependencies:

```bash
npm install
```

Configure the backend API URL:

```env
VITE_API_URL=http://127.0.0.1:8000
```

Start the frontend:

```bash
npm run dev
```

The frontend normally runs at:

```text
http://localhost:5173
```

---

# Running the Application

The local application architecture is:

```text
Browser
   │
   ▼
React + Vite
   │
   │ REST API
   ▼
FastAPI Backend
   │
   ├── Authentication
   ├── Resume Processing
   ├── Rule-Based Analysis
   ├── ML Analysis
   ├── Gemini AI
   └── Database
```

Start the backend first and then start the frontend.

---

# Production Build

The frontend production build can be created using:

```bash
npm run build
```

The production files are generated in:

```text
frontend/dist/
```

The production build should be tested before deployment.

---

# Deployment Architecture

The intended deployment architecture is:

```text
                    Internet
                       │
             ┌─────────┴─────────┐
             │                   │
             ▼                   ▼
       Vercel Frontend      Render Backend
             │                   │
             │ REST API          │
             └─────────►─────────┘
                                 │
                   ┌─────────────┼─────────────┐
                   │             │             │
                   ▼             ▼             ▼
               Database      Gemini API     Analysis
```

## Frontend — Vercel

The React frontend can be deployed to Vercel.

Production environment variable:

```env
VITE_API_URL=<your-backend-url>
```

---

## Backend — Render

The FastAPI backend can be deployed to Render.

Production start command:

```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

Backend environment variables should be configured through the hosting provider's environment-variable settings.

---

# Security

Security is an important part of ResumeIQ.

## Gemini API Key

The Gemini API key must:

- Stay on the backend.
- Be stored as an environment variable.
- Never be included in React code.
- Never be included in frontend environment variables.
- Never be committed to GitHub.
- Never be exposed in the browser.

The frontend communicates with the backend API rather than directly using the Gemini API key.

---

## `.env` Protection

The project uses `.gitignore` rules to prevent environment files from being committed:

```gitignore
.env
.env.*
```

---

## Database Protection

The local database is also excluded:

```gitignore
database/*.db
```

Therefore, local user data and database records are not intended to be uploaded to GitHub.

---

# Testing

The backend contains a testing directory:

```text
backend/tests/
```

Current testing can be extended to cover:

- Authentication
- Resume parsing
- Section detection
- Rule-based scoring
- ML scoring
- Job matching
- Analysis history
- PDF generation
- API endpoints

---

# Current Limitations

ResumeIQ is currently a portfolio/deployment-oriented project and has areas that can be improved in future versions.

Current limitations include:

- Real subscription payment processing is not implemented.
- Pro subscription currently represents the premium access flow.
- SQLite is currently used as the database.
- The ML semantic analysis currently uses TF-IDF and cosine similarity.
- Resume parsing accuracy may vary depending on document formatting.
- AI recommendations depend on the quality of the resume and job description.
- More advanced multilingual semantic analysis can be added in future versions.

---

# Future Improvements

## Real Payment Integration

Integrate a payment provider to support:

- Subscription plans
- Payment verification
- Subscription expiry
- Billing history
- Automatic Pro access management

---

## Advanced Semantic Models

The current TF-IDF-based semantic matching can be extended using:

- Sentence Transformers
- Embedding models
- Transformer-based semantic models
- Vector databases

---

## Resume Rewriting

Future versions could allow users to generate improved:

- Professional summaries
- Experience descriptions
- Project descriptions
- Skills sections

---

## Job Recommendation

The platform could recommend jobs based on:

- Skills
- Experience
- Projects
- Education
- Semantic job matching

---

## Resume Version Management

Users could maintain multiple resume versions for different roles.

Example:

```text
Resume
 ├── Software Developer
 ├── Data Analyst
 ├── Machine Learning
 └── Backend Developer
```

---

## Advanced Analytics Dashboard

Future analytics could include:

- Score improvement over time
- Job match history
- Missing skill trends
- Resume improvement trends
- Analysis statistics

---

## Production Database

SQLite can be migrated to PostgreSQL or another managed relational database for improved persistence and scalability.

---

# Project Goals

ResumeIQ was created to demonstrate the integration of multiple software engineering and AI/ML concepts in a single full-stack application.

The project combines:

```text
Frontend Development
        +
Backend Development
        +
REST API
        +
Authentication
        +
Database Management
        +
Document Processing
        +
Rule-Based Systems
        +
Machine Learning
        +
Natural Language Processing
        +
Generative AI
        +
PDF Generation
        +
Cloud Deployment
```

This makes ResumeIQ more than a simple resume-scoring application.

It demonstrates how different technologies can be integrated into an end-to-end software system.

---

# Conclusion

ResumeIQ is a full-stack resume analysis and job-matching platform that combines:

- Rule-based analysis
- Machine learning
- AI-powered recommendations
- Resume parsing
- Job matching
- Authentication
- Database management
- PDF report generation

The platform separates its analysis into two main modes.

### Normal Mode

```text
Rule-Based Analysis
        ↓
Resume Evaluation
        ↓
Scores + Feedback
```

### Pro Mode

```text
ML-Based Semantic Analysis
        ↓
Strong / Weak Area Detection
        ↓
AI-Powered Recommendations
        ↓
Structured PDF Improvement Report
```

Pro Mode provides **5 free analyses per user**, after which a subscription is required.

The current project does not implement a real payment gateway, leaving the payment layer open for future integration.

ResumeIQ is designed as a foundation for a more advanced intelligent career-assistance platform with future support for stronger semantic models, automated resume rewriting, job recommendations, real subscription infrastructure, and scalable cloud databases.

---

# Author

**Subhabrata Pal**

B.Tech Computer Science & Engineering  
Techno India University, Kolkata

---

# Project Status

**Active Development / Deployment**

ResumeIQ demonstrates practical implementation of:

- Full-Stack Web Development
- React.js
- FastAPI
- REST API Development
- Authentication
- Database Integration
- Document Processing
- Rule-Based Systems
- Machine Learning
- Natural Language Processing
- Generative AI
- PDF Generation
- Cloud Deployment