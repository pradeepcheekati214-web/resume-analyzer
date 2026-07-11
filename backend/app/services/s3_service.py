import uuid
import boto3
from botocore.exceptions import ClientError

from app.core.config import settings


class S3Service:
    def __init__(self):
        self.bucket_name = settings.S3_BUCKET_NAME

        self.s3 = boto3.client(
            "s3",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION,
        )

    def upload_file(self, file, filename):
        try:
            unique_filename = f"resumes/{uuid.uuid4()}_{filename}"

            self.s3.upload_fileobj(
                file,
                self.bucket_name,
                unique_filename,
                ExtraArgs={
                    "ContentType": "application/pdf"
                },
            )

            return f"https://{self.bucket_name}.s3.{settings.AWS_REGION}.amazonaws.com/{unique_filename}"

        except ClientError as e:
            raise Exception(f"S3 Upload Failed: {e}")


s3_service = S3Service()
