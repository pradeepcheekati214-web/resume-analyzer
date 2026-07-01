#!/usr/bin/env python3
"""
CDK App entry point — deploys all Resume Analyzer infrastructure stacks.

Usage:
    cdk deploy --all
    cdk deploy ResumeAnalyzerStorageStack
    cdk diff
"""
import aws_cdk as cdk

from stacks.storage_stack import StorageStack
from stacks.auth_stack import AuthStack
from stacks.api_stack import ApiStack
from stacks.monitoring_stack import MonitoringStack

app = cdk.App()

env = cdk.Environment(
    account=app.node.try_get_context("account") or "123456789012",
    region=app.node.try_get_context("region")  or "us-east-1",
)

# Deploy in dependency order
storage_stack = StorageStack(app, "ResumeAnalyzerStorageStack", env=env)
auth_stack    = AuthStack(app, "ResumeAnalyzerAuthStack",    env=env)
api_stack     = ApiStack(
    app, "ResumeAnalyzerApiStack",
    resume_bucket=storage_stack.resume_bucket,
    analysis_table=storage_stack.analysis_table,
    user_pool=auth_stack.user_pool,
    env=env,
)
monitoring_stack = MonitoringStack(
    app, "ResumeAnalyzerMonitoringStack",
    api_function=api_stack.api_function,
    env=env,
)

# Tag all resources
for stack in [storage_stack, auth_stack, api_stack, monitoring_stack]:
    cdk.Tags.of(stack).add("Project",     "ResumeAnalyzer")
    cdk.Tags.of(stack).add("Environment", app.node.try_get_context("env") or "dev")
    cdk.Tags.of(stack).add("ManagedBy",   "CDK")

app.synth()
