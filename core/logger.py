import structlog
from structlog.contextvars import merge_contextvars
import logging
from core.config import settings

structlog.configure(
    processors=[
        merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer(),
    ],
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
)

logging.basicConfig(level=settings.log_level)
logger = structlog.get_logger("ai_assessment")