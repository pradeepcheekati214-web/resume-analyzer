# Resume Analyzer

A full-stack AI-powered Resume Analyzer that provides ATS scoring, skills extraction, keyword analysis, and actionable improvement suggestions.

## Architecture Overview

```
resume-analyzer/
├── frontend/          # React.js + Vite application
├── backend/           # Python FastAPI application
├── infrastructure/    # AWS CDK infrastructure as code
├── docs/              # Documentation and API specs
├── docker-compose.yml # Local development environment
└── README.md
```

## Tech Stack

### Frontend
- **React.js** with Vite build tool
- **React Router v6** for navigation
- **Axios** for HTTP requests
- **React Dropzone** for file uploads
- **Recharts** for data visualization
- **Tailwind CSS** for styling

### Backend
- **Python 3.11** with FastAPI
- **pdfplumber** for PDF parsing
- **python-docx** for DOCX parsing
- **spaCy / NLTK** for NLP processing
- **boto3** for AWS SDK
- **JWT** authentication

### AWS Services
- **Amazon S3** — Resume file storage
- **AWS Lambda** — Serverless resume processing
- **Amazon API Gateway** — REST API management
- **Amazon DynamoDB** — Analysis results storage
- **Amazon Cognito** — User authentication
- **Amazon CloudWatch** — Logging and monitoring
- **AWS IAM** — Roles and permissions

---

## Prerequisites

- Node.js >= 18.x
- Python >= 3.11
- Docker & Docker Compose
- AWS CLI configured (`aws configure`)
- AWS CDK CLI (`npm install -g aws-cdk`)

---

## Quick Start (Local Development)

### 1. Clone the repository
```bash
git clone https://github.com/your-org/resume-analyzer.git
cd resume-analyzer
```

### 2. Set up environment variables
```bash
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
# Edit both .env files with your values
```

### 3. Start with Docker Compose
```bash
docker-compose up --build
```

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

---

## Manual Setup

### Backend
```bash
cd backend
python -m venv venv
# Windows: venv\Scripts\activate  |  macOS/Linux: source venv/bin/activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm
uvicorn app.main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

---

## AWS Deployment

```bash
# Deploy infrastructure
cd infrastructure
pip install -r requirements.txt
cdk bootstrap aws://ACCOUNT_ID/REGION
cdk deploy --all

# Deploy frontend to S3/CloudFront
cd ../frontend
npm run build
aws s3 sync dist/ s3://YOUR_FRONTEND_BUCKET --delete
```

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/register` | Register new user |
| POST | `/api/v1/auth/login` | Login and get JWT token |
| POST | `/api/v1/auth/refresh` | Refresh access token |
| POST | `/api/v1/resumes/upload` | Upload resume file |
| POST | `/api/v1/resumes/{id}/analyze` | Analyze uploaded resume |
| GET | `/api/v1/resumes/` | List user's resumes |
| GET | `/api/v1/resumes/{id}` | Get resume details |
| GET | `/api/v1/analysis/{id}` | Get analysis results |
| GET | `/api/v1/analysis/history` | Get analysis history |
| GET | `/api/v1/users/profile` | Get user profile |
| PUT | `/api/v1/users/profile` | Update user profile |

Full Swagger UI at `/docs`.

---

## Testing

```bash
# Backend
cd backend && pytest tests/ -v --cov=app

# Frontend
cd frontend && npm run test
```

---

## License

MIT License
