from datetime import datetime, timezone
from logging import config as logging_config  # pylint: disable=E0611

import structlog
from pythonjsonlogger import jsonlogger

config = {
    "version": 1,
    "formatters": {
        "json": {
            "()": "solarpark.logging.log_config.JsonFormatter",
            "format": "%(message)s %(levelname)s %(name)s",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
            "formatter": "json",
        }
    },
    "loggers": {
        "uvicorn.error": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        "uvicorn.access": {
            "handlers": ["console"],
            "level": "WARNING",
            "propagate": False,
        },
        "azure": {"level": "WARNING"},
        "uamqp": {"level": "WARNING"},
    },
    "root": {"level": "INFO", "handlers": ["console"]},
}


class JsonFormatter(jsonlogger.JsonFormatter):
    _allowed_fields = ["level", "message", "stack_trace", "timestamp", "exception", "logger", "name", "branchId"]

    def add_fields(self, log_record, record, message_dict):
        super().add_fields(log_record, record, message_dict)
        JsonFormatter._rename_field(log_record, "levelname", "level", transform=str.lower)
        JsonFormatter._rename_field(log_record, "stack", "stack_trace")
        JsonFormatter._rename_field(log_record, "exc_info", "exception")
        log_record["timestamp"] = datetime.now(timezone.utc)

        keys = list(log_record.keys())
        for key in keys:
            if key not in JsonFormatter._allowed_fields:
                log_record.pop(key)

    @staticmethod
    def _rename_field(log_record, from_key, to_key, transform=lambda x: x):
        value = log_record.pop(from_key, False)
        if value:
            log_record[to_key] = transform(value)


def configure_logging():
    logging_config.dictConfig(config)
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.stdlib.render_to_log_kwargs,
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )


def clear_thread_logging_state():
    structlog.contextvars.clear_contextvars()


def bind(**kwargs):
    structlog.contextvars.bind_contextvars(**kwargs)
