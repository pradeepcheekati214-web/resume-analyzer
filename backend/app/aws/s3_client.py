"""
Amazon S3 client — upload, download, delete, and presigned URL generation.
"""
import logging
import mimetypes
import uuid
from typing import Tuple

import boto3
from botocore.exceptions import ClientError

from app.core.config import settings

logger = logging.getLogger(__name__)


def _get_s3_client():
    return boto3.client(
        "s3",
        region_name=settings.AWS_REGION,
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    )


def upload_file_to_s3(
    file_bytes: bytes,
    filename: str,
    user_id: str,
    content_type: str = "application/octet-stream",
) -> Tuple[str, str]:
    """
    Upload a file to S3.

    Returns: (s3_key, presigned_url)
    """
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else "bin"
    s3_key = f"resumes/{user_id}/{uuid.uuid4()}.{ext}"

    client = _get_s3_client()
    client.put_object(
        Bucket=settings.S3_BUCKET_NAME,
        Key=s3_key,
        Body=file_bytes,
        ContentType=content_type,
        ServerSideEncryption="AES256",
        Metadata={"original_filename": filename, "user_id": user_id},
    )

    presigned_url = generate_presigned_url(s3_key)
    logger.info("Uploaded to S3: %s", s3_key)
    return s3_key, presigned_url


def download_file_from_s3(s3_key: str) -> bytes:
    """Download a file from S3 and return its bytes."""
    client = _get_s3_client()
    try:
        response = client.get_object(Bucket=settings.S3_BUCKET_NAME, Key=s3_key)
        return response["Body"].read()
    except ClientError as exc:
        logger.error("S3 download failed for key %s: %s", s3_key, exc)
        raise


def delete_file_from_s3(s3_key: str) -> None:
    """Delete a file from S3."""
    client = _get_s3_client()
    try:
        client.delete_object(Bucket=settings.S3_BUCKET_NAME, Key=s3_key)
        logger.info("Deleted from S3: %s", s3_key)
    except ClientError as exc:
        logger.error("S3 delete failed for key %s: %s", s3_key, exc)
        raise


def generate_presigned_url(s3_key: str, expiry: int = None) -> str:
    """Generate a presigned URL for reading a private S3 object."""
    expiry = expiry or settings.S3_PRESIGNED_URL_EXPIRY
    client = _get_s3_client()
    try:
        url = client.generate_presigned_url(
            "get_object",
            Params={"Bucket": settings.S3_BUCKET_NAME, "Key": s3_key},
            ExpiresIn=expiry,
        )
        return url
    except ClientError as exc:
        logger.error("Failed to generate presigned URL for %s: %s", s3_key, exc)
        raise


def list_user_files(user_id: str) -> list:
    """List all S3 objects under a user's prefix."""
    client = _get_s3_client()
    prefix = f"resumes/{user_id}/"
    try:
        response = client.list_objects_v2(Bucket=settings.S3_BUCKET_NAME, Prefix=prefix)
        return response.get("Contents", [])
    except ClientError as exc:
        logger.error("S3 list failed for user %s: %s", user_id, exc)
        return []
