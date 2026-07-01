"""
Monitoring Stack — CloudWatch alarms and dashboard.
"""
import aws_cdk as cdk
from aws_cdk import (
    Stack,
    Duration,
    aws_cloudwatch as cloudwatch,
    aws_cloudwatch_actions as cw_actions,
    aws_sns as sns,
    aws_lambda as lambda_,
)
from constructs import Construct


class MonitoringStack(Stack):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        api_function: lambda_.Function,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # ── SNS topic for alerts ──────────────────────────────────────────
        alert_topic = sns.Topic(
            self, "AlertTopic",
            topic_name="resume-analyzer-alerts",
            display_name="Resume Analyzer Alerts",
        )

        # ── Lambda error alarm ────────────────────────────────────────────
        error_alarm = cloudwatch.Alarm(
            self, "LambdaErrorAlarm",
            alarm_name="resume-analyzer-lambda-errors",
            alarm_description="Lambda function errors exceeded threshold.",
            metric=api_function.metric_errors(period=Duration.minutes(5)),
            threshold=5,
            evaluation_periods=1,
            comparison_operator=cloudwatch.ComparisonOperator.GREATER_THAN_OR_EQUAL_TO_THRESHOLD,
            treat_missing_data=cloudwatch.TreatMissingData.NOT_BREACHING,
        )
        error_alarm.add_alarm_action(cw_actions.SnsAction(alert_topic))

        # ── Lambda duration alarm ─────────────────────────────────────────
        duration_alarm = cloudwatch.Alarm(
            self, "LambdaDurationAlarm",
            alarm_name="resume-analyzer-lambda-duration",
            alarm_description="Lambda p99 duration exceeded 25 seconds.",
            metric=api_function.metric_duration(
                period=Duration.minutes(5),
                statistic="p99",
            ),
            threshold=25000,  # ms
            evaluation_periods=2,
            comparison_operator=cloudwatch.ComparisonOperator.GREATER_THAN_THRESHOLD,
            treat_missing_data=cloudwatch.TreatMissingData.NOT_BREACHING,
        )

        # ── CloudWatch Dashboard ──────────────────────────────────────────
        dashboard = cloudwatch.Dashboard(
            self, "Dashboard",
            dashboard_name="ResumeAnalyzer",
        )
        dashboard.add_widgets(
            cloudwatch.GraphWidget(
                title="Lambda Invocations & Errors",
                left=[api_function.metric_invocations(period=Duration.minutes(5))],
                right=[api_function.metric_errors(period=Duration.minutes(5))],
                width=12,
            ),
            cloudwatch.GraphWidget(
                title="Lambda Duration (p50 / p99)",
                left=[
                    api_function.metric_duration(period=Duration.minutes(5), statistic="p50"),
                    api_function.metric_duration(period=Duration.minutes(5), statistic="p99"),
                ],
                width=12,
            ),
            cloudwatch.SingleValueWidget(
                title="Lambda Throttles",
                metrics=[api_function.metric_throttles(period=Duration.minutes(5))],
                width=6,
            ),
            cloudwatch.SingleValueWidget(
                title="Lambda Concurrent Executions",
                metrics=[api_function.metric(
                    "ConcurrentExecutions",
                    period=Duration.minutes(5),
                    statistic="Maximum",
                )],
                width=6,
            ),
        )

        # ── Outputs ───────────────────────────────────────────────────────
        cdk.CfnOutput(self, "AlertTopicArn", value=alert_topic.topic_arn)
        cdk.CfnOutput(self, "DashboardUrl",
            value=f"https://console.aws.amazon.com/cloudwatch/home?region={self.region}#dashboards:name=ResumeAnalyzer"
        )
