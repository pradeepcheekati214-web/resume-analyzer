"""
Logging configuration — structured JSON logs in production, readable in dev.
"""
import logging
import sys
from app.core.config import settings

LOG_LEVEL = logging.DEBUG if settings.DEBUG else logging.INFO


def configure_logging():
    fmt = (
        "%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d | %(message)s"
        if settings.APP_ENV != "production"
        else '{"time":"%(asctime)s","level":"%(levelname)s","logger":"%(name)s","msg":"%(message)s"}'
    )

    logging.basicConfig(
        level=LOG_LEVEL,
        format=fmt,
        handlers=[logging.StreamHandler(sys.stdout)],
    )

    # Quieten noisy third-party loggers
    for noisy in ("botocore", "boto3", "urllib3", "s3transfer"):
        logging.getLogger(noisy).setLevel(logging.WARNING)


configure_logging()
