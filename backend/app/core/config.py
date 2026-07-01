"""
Application configuration loaded from environment variables / .env file.
"""
from typing import List, Union
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # App
    APP_ENV: str = "development"
    APP_NAME: str = "Resume Analyzer API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # CORS — accepts either a list or a comma-separated string from .env
    ALLOWED_ORIGINS: Union[List[str], str] = [
        "http://localhost:5173",
        "http://localhost:3000",
    ]

    @field_validator("ALLOWED_ORIGINS", mode="before")
    @classmethod
    def parse_allowed_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v

    # Security
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Database
    DATABASE_URL: str = "sqlite:///./resume_analyzer.db"

    # AWS
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    AWS_REGION: str = "us-east-1"
    S3_BUCKET_NAME: str = "resume-analyzer-files-dev"
    S3_PRESIGNED_URL_EXPIRY: int = 3600

    # DynamoDB
    DYNAMODB_TABLE_NAME: str = "resume-analyzer-results"
    DYNAMODB_ENDPOINT_URL: str = ""

    # Cognito
    COGNITO_USER_POOL_ID: str = ""
    COGNITO_CLIENT_ID: str = ""
    COGNITO_REGION: str = "us-east-1"

    # File upload
    MAX_UPLOAD_SIZE_MB: int = 10
    ALLOWED_EXTENSIONS: Union[List[str], str] = [".pdf", ".docx", ".doc"]

    @field_validator("ALLOWED_EXTENSIONS", mode="before")
    @classmethod
    def parse_allowed_extensions(cls, v):
        if isinstance(v, str):
            return [ext.strip() for ext in v.split(",") if ext.strip()]
        return v

    # AI / LLM
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-3.5-turbo"
    AWS_BEDROCK_MODEL_ID: str = "anthropic.claude-3-sonnet-20240229-v1:0"
    AI_PROVIDER: str = "mock"   # openai | bedrock | mock
    AI_MAX_TOKENS: int = 2000
    AI_TEMPERATURE: float = 0.7

    @property
    def ai_enabled(self) -> bool:
        return bool(
            (self.AI_PROVIDER == "openai" and self.OPENAI_API_KEY) or
            (self.AI_PROVIDER == "bedrock" and self.is_aws_configured)
        )

    # CloudWatch
    CLOUDWATCH_LOG_GROUP: str = "resume-analyzer"
    CLOUDWATCH_LOG_STREAM: str = "api"

    @property
    def max_upload_size_bytes(self) -> int:
        return self.MAX_UPLOAD_SIZE_MB * 1024 * 1024

    @property
    def is_aws_configured(self) -> bool:
        return bool(self.AWS_ACCESS_KEY_ID and self.AWS_SECRET_ACCESS_KEY)


settings = Settings()
