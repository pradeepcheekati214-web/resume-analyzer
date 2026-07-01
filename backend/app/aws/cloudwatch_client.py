"""
Amazon CloudWatch logging integration.
Sends structured log events to CloudWatch Logs.
"""
import json
import logging
import time
from typing import Optional

import boto3
from botocore.exceptions import ClientError

from app.core.config import settings

logger = logging.getLogger(__name__)

_log_client = None
_sequence_token: Optional[str] = None


def _get_client():
    global _log_client
    if _log_client is None:
        _log_client = boto3.client(
            "logs",
            region_name=settings.AWS_REGION,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        )
    return _log_client


def _ensure_log_group_and_stream():
    """Create log group and stream if they don't exist."""
    client = _get_client()
    try:
        client.create_log_group(logGroupName=settings.CLOUDWATCH_LOG_GROUP)
    except client.exceptions.ResourceAlreadyExistsException:
        pass

    try:
        client.create_log_stream(
            logGroupName=settings.CLOUDWATCH_LOG_GROUP,
            logStreamName=settings.CLOUDWATCH_LOG_STREAM,
        )
    except client.exceptions.ResourceAlreadyExistsException:
        pass


def send_log_event(message: dict, level: str = "INFO") -> None:
    """Send a single structured log event to CloudWatch."""
    if not settings.is_aws_configured:
        return

    global _sequence_token
    try:
        _ensure_log_group_and_stream()
        client = _get_client()

        event = {
            "timestamp": int(time.time() * 1000),
            "message": json.dumps({"level": level, **message}),
        }

        kwargs = {
            "logGroupName": settings.CLOUDWATCH_LOG_GROUP,
            "logStreamName": settings.CLOUDWATCH_LOG_STREAM,
            "logEvents": [event],
        }
        if _sequence_token:
            kwargs["sequenceToken"] = _sequence_token

        response = client.put_log_events(**kwargs)
        _sequence_token = response.get("nextSequenceToken")

    except ClientError as exc:
        logger.warning("CloudWatch log failed: %s", exc)


def log_analysis_event(user_id: str, analysis_id: str, ats_score: float, status: str) -> None:
    """Log an analysis completion event to CloudWatch."""
    send_log_event({
        "event": "analysis_completed",
        "user_id": user_id,
        "analysis_id": analysis_id,
        "ats_score": ats_score,
        "status": status,
    })


def log_upload_event(user_id: str, resume_id: str, file_name: str, file_size: int) -> None:
    """Log a resume upload event to CloudWatch."""
    send_log_event({
        "event": "resume_uploaded",
        "user_id": user_id,
        "resume_id": resume_id,
        "file_name": file_name,
        "file_size": file_size,
    })
