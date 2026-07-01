"""
Storage Stack — S3 bucket for resumes + DynamoDB table for analysis results.
"""
import aws_cdk as cdk
from aws_cdk import (
    Stack,
    aws_s3 as s3,
    aws_dynamodb as dynamodb,
    RemovalPolicy,
)
from constructs import Construct


class StorageStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # ── S3 Bucket ─────────────────────────────────────────────────────
        self.resume_bucket = s3.Bucket(
            self, "ResumeBucket",
            bucket_name=f"resume-analyzer-files-{self.account}-{self.region}",
            versioned=True,
            encryption=s3.BucketEncryption.S3_MANAGED,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            removal_policy=RemovalPolicy.RETAIN,
            lifecycle_rules=[
                s3.LifecycleRule(
                    id="DeleteOldVersions",
                    noncurrent_version_expiration=cdk.Duration.days(30),
                ),
            ],
            cors=[
                s3.CorsRule(
                    allowed_methods=[s3.HttpMethods.GET, s3.HttpMethods.PUT, s3.HttpMethods.POST],
                    allowed_origins=["*"],   # Tighten to your domain in production
                    allowed_headers=["*"],
                    max_age=3000,
                )
            ],
        )

        # ── DynamoDB Table ────────────────────────────────────────────────
        self.analysis_table = dynamodb.Table(
            self, "AnalysisTable",
            table_name="resume-analyzer-results",
            partition_key=dynamodb.Attribute(name="PK", type=dynamodb.AttributeType.STRING),
            sort_key=dynamodb.Attribute(name="SK", type=dynamodb.AttributeType.STRING),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.RETAIN,
            point_in_time_recovery=True,
            # TTL for automatic expiry of old analyses (optional)
            time_to_live_attribute="ttl",
        )

        # GSI for direct analysis lookup by analysis ID
        self.analysis_table.add_global_secondary_index(
            index_name="GSI1",
            partition_key=dynamodb.Attribute(name="GSI1PK", type=dynamodb.AttributeType.STRING),
            projection_type=dynamodb.ProjectionType.ALL,
        )

        # ── Outputs ───────────────────────────────────────────────────────
        cdk.CfnOutput(self, "ResumeBucketName",    value=self.resume_bucket.bucket_name)
        cdk.CfnOutput(self, "AnalysisTableName",   value=self.analysis_table.table_name)
        cdk.CfnOutput(self, "ResumeBucketArn",     value=self.resume_bucket.bucket_arn)
