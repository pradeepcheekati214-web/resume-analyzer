"""
Auth Stack — Amazon Cognito User Pool for authentication.
"""
import aws_cdk as cdk
from aws_cdk import (
    Stack,
    aws_cognito as cognito,
    RemovalPolicy,
    Duration,
)
from constructs import Construct


class AuthStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # ── User Pool ─────────────────────────────────────────────────────
        self.user_pool = cognito.UserPool(
            self, "UserPool",
            user_pool_name="resume-analyzer-users",
            self_sign_up_enabled=True,
            sign_in_aliases=cognito.SignInAliases(email=True, username=False),
            auto_verify=cognito.AutoVerifiedAttrs(email=True),
            standard_attributes=cognito.StandardAttributes(
                email=cognito.StandardAttribute(required=True, mutable=True),
                fullname=cognito.StandardAttribute(required=False, mutable=True),
            ),
            password_policy=cognito.PasswordPolicy(
                min_length=8,
                require_lowercase=True,
                require_uppercase=True,
                require_digits=True,
                require_symbols=False,
                temp_password_validity=Duration.days(7),
            ),
            account_recovery=cognito.AccountRecovery.EMAIL_ONLY,
            removal_policy=RemovalPolicy.RETAIN,
            # Email configuration (use SES in production)
            email=cognito.UserPoolEmail.with_cognito(
                reply_to="noreply@resumeanalyzer.example.com"
            ),
        )

        # ── App Client ────────────────────────────────────────────────────
        self.user_pool_client = self.user_pool.add_client(
            "WebClient",
            user_pool_client_name="resume-analyzer-web",
            auth_flows=cognito.AuthFlow(
                user_password=True,
                user_srp=True,
            ),
            o_auth=cognito.OAuthSettings(
                flows=cognito.OAuthFlows(authorization_code_grant=True),
                scopes=[
                    cognito.OAuthScope.EMAIL,
                    cognito.OAuthScope.OPENID,
                    cognito.OAuthScope.PROFILE,
                ],
                callback_urls=["http://localhost:5173/callback", "https://your-domain.com/callback"],
                logout_urls=["http://localhost:5173/login", "https://your-domain.com/login"],
            ),
            access_token_validity=Duration.minutes(30),
            id_token_validity=Duration.minutes(30),
            refresh_token_validity=Duration.days(7),
            prevent_user_existence_errors=True,
        )

        # ── Identity Pool (for direct AWS access from frontend if needed) ─
        self.identity_pool = cognito.CfnIdentityPool(
            self, "IdentityPool",
            identity_pool_name="resume_analyzer_identity_pool",
            allow_unauthenticated_identities=False,
            cognito_identity_providers=[
                cognito.CfnIdentityPool.CognitoIdentityProviderProperty(
                    client_id=self.user_pool_client.user_pool_client_id,
                    provider_name=self.user_pool.user_pool_provider_name,
                )
            ],
        )

        # ── Outputs ───────────────────────────────────────────────────────
        cdk.CfnOutput(self, "UserPoolId",       value=self.user_pool.user_pool_id)
        cdk.CfnOutput(self, "UserPoolClientId", value=self.user_pool_client.user_pool_client_id)
        cdk.CfnOutput(self, "IdentityPoolId",   value=self.identity_pool.ref)
