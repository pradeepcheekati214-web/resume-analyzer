from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, ConfigDict, Field


# ---------------------------------------------------------------------------
# Single question shape
# ---------------------------------------------------------------------------
class InterviewQuestion(BaseModel):
    id: int
    question: str
    category: str
    difficulty: str = "medium"   # easy | medium | hard
    tips: Optional[str] = None
    expected_keywords: Optional[List[str]] = None


# ---------------------------------------------------------------------------
# Question Set
# ---------------------------------------------------------------------------
class QuestionSetCreate(BaseModel):
    resume_id: str
    job_title: Optional[str] = None
    job_description: Optional[str] = None
    company_name: Optional[str] = None
    categories: Optional[List[str]] = None


class QuestionSetRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    owner_id: str
    resume_id: str
    job_title: Optional[str] = None
    company_name: Optional[str] = None
    job_description: Optional[str] = None
    status: str
    error_message: Optional[str] = None
    total_questions: int = 0

    technical_questions: Optional[List[Dict[str, Any]]] = None
    behavioral_questions: Optional[List[Dict[str, Any]]] = None
    hr_questions: Optional[List[Dict[str, Any]]] = None
    project_questions: Optional[List[Dict[str, Any]]] = None
    aws_questions: Optional[List[Dict[str, Any]]] = None
    python_questions: Optional[List[Dict[str, Any]]] = None
    react_questions: Optional[List[Dict[str, Any]]] = None
    database_questions: Optional[List[Dict[str, Any]]] = None

    created_at: datetime
    updated_at: datetime


# ---------------------------------------------------------------------------
# Mock Interview
# ---------------------------------------------------------------------------
class MockInterviewCreate(BaseModel):
    question_set_id: str
    mode: str = "text"


class MockInterviewRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    owner_id: str
    question_set_id: str
    status: str
    mode: str
    total_questions: int
    answered: int
    current_index: int

    overall_score: Optional[float] = None
    technical_score: Optional[float] = None
    communication_score: Optional[float] = None
    confidence_score: Optional[float] = None
    grammar_score: Optional[float] = None

    strengths: Optional[List[str]] = None
    weaknesses: Optional[List[str]] = None
    improvements: Optional[List[str]] = None
    overall_feedback: Optional[str] = None

    started_at: datetime
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


class NextQuestionResponse(BaseModel):
    interview_id: str
    question_index: int
    total_questions: int
    question: Dict[str, Any]
    is_last: bool
    time_limit_secs: int = 120


# ---------------------------------------------------------------------------
# Answer Submission
# ---------------------------------------------------------------------------
class AnswerSubmit(BaseModel):
    interview_id: str
    question_index: int
    question_text: str
    question_category: str
    question_difficulty: str = "medium"
    answer_text: str = Field(..., min_length=1)
    time_taken_secs: int = 0


class AnswerEvaluation(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    question_index: int
    question_text: str
    answer_text: str
    score: Optional[float] = None
    technical_accuracy: Optional[float] = None
    communication: Optional[float] = None
    completeness: Optional[float] = None
    feedback: Optional[str] = None
    ideal_answer: Optional[str] = None
    keywords_used: Optional[List[str]] = None
    keywords_missed: Optional[List[str]] = None
    created_at: datetime


# ---------------------------------------------------------------------------
# Interview Result
# ---------------------------------------------------------------------------
class InterviewResult(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    status: str
    total_questions: int
    answered: int
    overall_score: Optional[float] = None
    technical_score: Optional[float] = None
    communication_score: Optional[float] = None
    confidence_score: Optional[float] = None
    grammar_score: Optional[float] = None
    strengths: Optional[List[str]] = None
    weaknesses: Optional[List[str]] = None
    improvements: Optional[List[str]] = None
    overall_feedback: Optional[str] = None
    answers: Optional[List[Dict[str, Any]]] = None
    started_at: datetime
    completed_at: Optional[datetime] = None


# ---------------------------------------------------------------------------
# Interview History
# ---------------------------------------------------------------------------
class InterviewHistoryItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    interview_id: str
    job_title: Optional[str] = None
    total_questions: int
    overall_score: Optional[float] = None
    technical_score: Optional[float] = None
    communication_score: Optional[float] = None
    duration_minutes: Optional[float] = None
    passed: bool
    created_at: datetime


class InterviewHistoryList(BaseModel):
    items: List[InterviewHistoryItem]
    total: int
    page: int
    page_size: int
