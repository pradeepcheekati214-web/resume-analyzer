# Architecture Overview

## High-Level Architecture

```
                          ┌──────────────────────────────────────┐
                          │           AWS Cloud                   │
                          │                                       │
 ┌──────────┐   HTTPS     │  ┌─────────────┐   ┌─────────────┐  │
 │  Browser │ ──────────► │  │ CloudFront  │   │ API Gateway │  │
 │ (React)  │             │  │   + S3      │   │             │  │
 └──────────┘             │  │  (Frontend) │   └──────┬──────┘  │
                          │  └─────────────┘          │         │
                          │                            │ proxy   │
                          │                     ┌──────▼──────┐  │
                          │                     │   Lambda    │  │
                          │                     │  (FastAPI + │  │
                          │                     │   Mangum)   │  │
                          │                     └──────┬──────┘  │
                          │                            │         │
                          │         ┌──────────────────┼──────┐  │
                          │         │                  │      │  │
                          │  ┌──────▼──────┐   ┌──────▼────┐ │  │
                          │  │    S3       │   │ DynamoDB  │ │  │
                          │  │  (Resumes)  │   │(Analyses) │ │  │
                          │  └─────────────┘   └───────────┘ │  │
                          │         │                         │  │
                          │  ┌──────▼──────┐   ┌─────────────┘  │
                          │  │  Cognito    │   │  CloudWatch  │  │
                          │  │   (Auth)    │   │   (Logging)  │  │
                          │  └─────────────┘   └──────────────┘  │
                          └──────────────────────────────────────┘
```

## Request Flow

### Resume Upload & Analysis

1. User uploads resume via React frontend
2. Frontend `POST /api/v1/resumes/upload` (multipart/form-data)
3. API Gateway proxies to Lambda (FastAPI + Mangum)
4. Lambda validates file (type, size)
5. Lambda stores file in S3 (`resumes/{user_id}/{uuid}.pdf`)
6. Lambda returns resume ID
7. Frontend `POST /api/v1/resumes/{id}/analyze`
8. Lambda downloads file from S3
9. Lambda runs analysis pipeline:
   - Resume parsing (pdfplumber / python-docx)
   - Contact info extraction (regex)
   - Skills extraction (taxonomy matching)
   - ATS scoring algorithm (6 dimensions)
   - Suggestion generation
10. Results stored in DynamoDB + SQLite (dual write)
11. Analysis result returned to frontend
12. Frontend renders results page

## Data Flow

```
Upload → S3 → Lambda → [Parse → Extract → Score → Suggest] → DynamoDB → Response
```

## Security

- JWT tokens (HS256) for local auth; Cognito JWTs when deployed to AWS
- All S3 objects are private; access via presigned URLs (1-hour expiry)
- DynamoDB access restricted to Lambda execution role
- API Gateway throttling (1000 req/s)
- HTTPS only in production (CloudFront + ACM)
- Input validation on all endpoints (Pydantic)
- Parameterised queries via SQLAlchemy ORM

## Database Schema

### SQLite / PostgreSQL (via SQLAlchemy)

```
users
  id (PK), email (unique), full_name, hashed_password, is_active, created_at

resumes
  id (PK), owner_id (FK→users), file_name, file_type, file_size,
  s3_key, s3_url, raw_text, word_count, page_count, created_at

analyses
  id (PK), resume_id (FK→resumes), owner_id (FK→users),
  status, ats_score, score_breakdown (JSON), skills_found (JSON),
  missing_skills (JSON), suggestions (JSON), contact_info (JSON),
  keywords_matched, skills_count, missing_count, created_at
```

### DynamoDB (single-table design)

```
PK: USER#{user_id}
SK: ANALYSIS#{analysis_id}
GSI1: GSI1PK = ANALYSIS#{analysis_id}   (for direct ID lookups)
```
