"""
Amazon DynamoDB client — persist and retrieve analysis results.

Table schema (single-table design):
  PK: USER#{user_id}
  SK: ANALYSIS#{analysis_id}
  GSI1PK: ANALYSIS#{analysis_id}  (for direct lookups)
"""
import logging
from decimal import Decimal
from typing import Optional

import boto3
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError

from app.core.config import settings

logger = logging.getLogger(__name__)


def _get_table():
    kwargs = {
        "region_name": settings.AWS_REGION,
        "aws_access_key_id": settings.AWS_ACCESS_KEY_ID,
        "aws_secret_access_key": settings.AWS_SECRET_ACCESS_KEY,
    }
    if settings.DYNAMODB_ENDPOINT_URL:
        kwargs["endpoint_url"] = settings.DYNAMODB_ENDPOINT_URL

    dynamodb = boto3.resource("dynamodb", **kwargs)
    return dynamodb.Table(settings.DYNAMODB_TABLE_NAME)


def _float_to_decimal(obj):
    """Recursively convert floats to Decimal for DynamoDB compatibility."""
    if isinstance(obj, float):
        return Decimal(str(obj))
    if isinstance(obj, dict):
        return {k: _float_to_decimal(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_float_to_decimal(i) for i in obj]
    return obj


def save_analysis_to_dynamo(analysis, resume) -> None:
    """Persist an analysis record to DynamoDB."""
    table = _get_table()
    item = {
        "PK": f"USER#{analysis.owner_id}",
        "SK": f"ANALYSIS#{analysis.id}",
        "GSI1PK": f"ANALYSIS#{analysis.id}",
        "id": analysis.id,
        "resume_id": analysis.resume_id,
        "owner_id": analysis.owner_id,
        "file_name": resume.file_name,
        "status": analysis.status,
        "ats_score": _float_to_decimal(analysis.ats_score or 0),
        "score_breakdown": _float_to_decimal(analysis.score_breakdown or {}),
        "skills_found": analysis.skills_found or [],
        "missing_skills": analysis.missing_skills or [],
        "keywords_matched": analysis.keywords_matched or 0,
        "contact_info": analysis.contact_info or {},
        "suggestions": analysis.suggestions or [],
        "skills_count": analysis.skills_count or 0,
        "missing_count": analysis.missing_count or 0,
        "created_at": analysis.created_at.isoformat(),
        "updated_at": analysis.updated_at.isoformat(),
    }
    try:
        table.put_item(Item=item)
        logger.info("Analysis saved to DynamoDB: %s", analysis.id)
    except ClientError as exc:
        logger.error("DynamoDB put_item failed: %s", exc)
        raise


def get_analysis_from_dynamo(analysis_id: str) -> Optional[dict]:
    """Retrieve an analysis by its ID using the GSI."""
    table = _get_table()
    try:
        response = table.query(
            IndexName="GSI1",
            KeyConditionExpression=Key("GSI1PK").eq(f"ANALYSIS#{analysis_id}"),
            Limit=1,
        )
        items = response.get("Items", [])
        return items[0] if items else None
    except ClientError as exc:
        logger.error("DynamoDB query failed for analysis %s: %s", analysis_id, exc)
        return None


def get_user_analyses_from_dynamo(user_id: str, limit: int = 10) -> list:
    """Retrieve all analyses for a user, sorted by created_at descending."""
    table = _get_table()
    try:
        response = table.query(
            KeyConditionExpression=Key("PK").eq(f"USER#{user_id}") & Key("SK").begins_with("ANALYSIS#"),
            ScanIndexForward=False,
            Limit=limit,
        )
        return response.get("Items", [])
    except ClientError as exc:
        logger.error("DynamoDB query failed for user %s: %s", user_id, exc)
        return []


def delete_analysis_from_dynamo(user_id: str, analysis_id: str) -> None:
    """Delete an analysis from DynamoDB."""
    table = _get_table()
    try:
        table.delete_item(
            Key={"PK": f"USER#{user_id}", "SK": f"ANALYSIS#{analysis_id}"}
        )
        logger.info("Analysis deleted from DynamoDB: %s", analysis_id)
    except ClientError as exc:
        logger.error("DynamoDB delete failed: %s", exc)
        raise


def ensure_table_exists() -> None:
    """
    Create the DynamoDB table if it doesn't exist (used in local dev / CDK bootstrap).
    In production, the table is managed by CDK.
    """
    client_kwargs = {
        "region_name": settings.AWS_REGION,
        "aws_access_key_id": settings.AWS_ACCESS_KEY_ID,
        "aws_secret_access_key": settings.AWS_SECRET_ACCESS_KEY,
    }
    if settings.DYNAMODB_ENDPOINT_URL:
        client_kwargs["endpoint_url"] = settings.DYNAMODB_ENDPOINT_URL

    client = boto3.client("dynamodb", **client_kwargs)
    try:
        client.describe_table(TableName=settings.DYNAMODB_TABLE_NAME)
        logger.debug("DynamoDB table already exists: %s", settings.DYNAMODB_TABLE_NAME)
    except client.exceptions.ResourceNotFoundException:
        client.create_table(
            TableName=settings.DYNAMODB_TABLE_NAME,
            KeySchema=[
                {"AttributeName": "PK", "KeyType": "HASH"},
                {"AttributeName": "SK", "KeyType": "RANGE"},
            ],
            AttributeDefinitions=[
                {"AttributeName": "PK", "AttributeType": "S"},
                {"AttributeName": "SK", "AttributeType": "S"},
                {"AttributeName": "GSI1PK", "AttributeType": "S"},
            ],
            GlobalSecondaryIndexes=[{
                "IndexName": "GSI1",
                "KeySchema": [{"AttributeName": "GSI1PK", "KeyType": "HASH"}],
                "Projection": {"ProjectionType": "ALL"},
                "BillingMode": "PAY_PER_REQUEST",
            }],
            BillingMode="PAY_PER_REQUEST",
        )
        logger.info("DynamoDB table created: %s", settings.DYNAMODB_TABLE_NAME)
