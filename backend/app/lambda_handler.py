"""
AWS Lambda entry point using Mangum to wrap the FastAPI ASGI app.

Deploy note:
  handler = app.lambda_handler.handler
"""
try:
    from mangum import Mangum
    from app.main import app

    # Lifespan=off because Lambda handles startup/shutdown differently
    handler = Mangum(app, lifespan="off")
except ImportError:
    # mangum is only needed in Lambda deployments; ignore in local dev
    handler = None
