"""
API Stack — Lambda function + API Gateway + IAM roles.
"""
import aws_cdk as cdk
from aws_cdk import (
    Stack,
    Duration,
    aws_lambda as lambda_,
    aws_apigateway as apigateway,
    aws_iam as iam,
    aws_s3 as s3,
    aws_dynamodb as dynamodb,
    aws_cognito as cognito,
    aws_logs as logs,
)
from constructs import Construct


class ApiStack(Stack):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        resume_bucket: s3.Bucket,
        analysis_table: dynamodb.Table,
        user_pool: cognito.UserPool,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # ── IAM Role ─────────────────────────────────────────────────────
        lambda_role = iam.Role(
            self, "LambdaExecutionRole",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaBasicExecutionRole"),
            ],
        )

        # Grant S3 and DynamoDB permissions
        resume_bucket.grant_read_write(lambda_role)
        analysis_table.grant_read_write_data(lambda_role)

        # CloudWatch Logs
        lambda_role.add_to_policy(iam.PolicyStatement(
            actions=["logs:CreateLogGroup", "logs:CreateLogStream", "logs:PutLogEvents"],
            resources=["*"],
        ))

        # ── Lambda Function ───────────────────────────────────────────────
        self.api_function = lambda_.Function(
            self, "ResumeAnalyzerFunction",
            function_name="resume-analyzer-api",
            runtime=lambda_.Runtime.PYTHON_3_11,
            handler="app.main.handler",   # Mangum adapter entry point
            code=lambda_.Code.from_asset(
                "../backend",
                exclude=["tests", "*.db", "__pycache__", ".env", "venv", ".venv"],
            ),
            role=lambda_role,
            timeout=Duration.seconds(30),
            memory_size=512,
            environment={
                "APP_ENV":          "production",
                "S3_BUCKET_NAME":   resume_bucket.bucket_name,
                "DYNAMODB_TABLE_NAME": analysis_table.table_name,
                "AWS_REGION":       self.region,
                # Secrets should come from SSM Parameter Store or Secrets Manager in production
                "SECRET_KEY":       "REPLACE_WITH_SSM_PARAMETER",
            },
            log_retention=logs.RetentionDays.ONE_MONTH,
        )

        # ── API Gateway ───────────────────────────────────────────────────
        # Cognito Authorizer
        cognito_authorizer = apigateway.CognitoUserPoolsAuthorizer(
            self, "CognitoAuthorizer",
            cognito_user_pools=[user_pool],
        )

        # Access log group
        access_log_group = logs.LogGroup(
            self, "ApiAccessLogs",
            retention=logs.RetentionDays.ONE_MONTH,
        )

        api = apigateway.RestApi(
            self, "ResumeAnalyzerApi",
            rest_api_name="resume-analyzer-api",
            description="Resume Analyzer REST API",
            deploy_options=apigateway.StageOptions(
                stage_name="v1",
                logging_level=apigateway.MethodLoggingLevel.INFO,
                data_trace_enabled=False,
                access_log_destination=apigateway.LogGroupLogDestination(access_log_group),
                access_log_format=apigateway.AccessLogFormat.json_with_standard_fields(
                    caller=True,
                    http_method=True,
                    ip=True,
                    protocol=True,
                    request_time=True,
                    resource_path=True,
                    response_length=True,
                    status=True,
                    user=True,
                ),
                throttling_rate_limit=1000,
                throttling_burst_limit=200,
            ),
            default_cors_preflight_options=apigateway.CorsOptions(
                allow_origins=apigateway.Cors.ALL_ORIGINS,
                allow_methods=apigateway.Cors.ALL_METHODS,
                allow_headers=["Content-Type", "Authorization"],
            ),
        )

        # Proxy all requests to Lambda
        lambda_integration = apigateway.LambdaIntegration(
            self.api_function,
            proxy=True,
            allow_test_invoke=False,
        )
        api.root.add_proxy(
            any_method=True,
            default_integration=lambda_integration,
        )

        # ── Outputs ───────────────────────────────────────────────────────
        cdk.CfnOutput(self, "ApiEndpoint",      value=api.url)
        cdk.CfnOutput(self, "LambdaFunctionArn", value=self.api_function.function_arn)
